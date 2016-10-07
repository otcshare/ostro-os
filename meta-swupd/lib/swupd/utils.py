

def manifest_to_file_list(manifest_fn):
    """
    Open a manifest file and read it into a list.
    Entries in the list are relative, i.e. no leading
    slash.

    manifest_fn -- the manifest file to read
    """
    image_manifest_list = []
    with open(manifest_fn) as image:
        image_manifest_list = [x[1:] for x in image.read().splitlines()]

    return image_manifest_list


def create_content_manifests(dir, included, excluded, blacklist):
    """
    Iterate over the content of the directory, decide which entries are
    included in the swupd update mechanism and write the absolute paths of the remaining
    entries (with leading slash) to the respective file. All directories
    are explicitly listed.
    """
    bb.debug(3, 'Creating %s and %s from directory %s, excluding %s' %
             (included, excluded, dir, blacklist))
    cwd = os.getcwd()
    try:
        os.chdir(dir)
        with open(included, 'w') as i:
            with open(excluded or '/dev/null', 'w') as e:
                for root, dirs, files in os.walk('.'):
                    # Strip the leading . that we get in root from os.walk('.').
                    # Resulting path must be absolute (for consistency with how
                    # swupd-server handles scanning real directories); this
                    # also matches the blacklist convention (also absolute).
                    root = '/' if root == '.' else root[1:]
                    for entry in sorted(dirs + files):
                        fullpath = os.path.join(root, entry)
                        out = e if blacklist and fullpath in blacklist else i
                        out.write(fullpath + '\n')
    finally:
        os.chdir(cwd)

def delta_contents(difflist):
    """
    Generate a list of files which exist in the bundle image but not the base
    image

    '- ' - line unique to lhs
    '+ ' - line unique to rhs
    '  ' - line common
    '? ' - line not present in either

    returns a list containing the items which are unique in the rhs

    difflist --- a list containing the output of difflib.Differ.compare
          where the lhs (left-hand-side) was the base image and the rhs
          (right-hand-side) was base image + extras (the bundle image).
    """
    cont = []
    for ln in difflist:
        if ln[0] == '+':
            cont.append(ln[3:])
    return cont


def unique_contents(base_manifest_fn, image_manifest_fn):
    """
    Get a list of files unique to the bundle image

    Compare the bundle image manifest to the base image manifest and return
    a list of files unique to the bundle image.

    base_manifest_fn -- the base image manifest
    image_manifest_fn -- the bundle image manifest
    """
    import difflib
    differ = difflib.Differ()

    base_manifest_list = []
    with open(base_manifest_fn) as base:
        base_manifest_list = base.read().splitlines()

    image_manifest_list = []
    with open(image_manifest_fn) as image:
        image_manifest_list = image.read().splitlines()

    delta = list(differ.compare(base_manifest_list, image_manifest_list))

    return delta_contents(delta)


# FIXME: Mariano proposed a similar method to OE-Core for package_manager
def get_package_manager(d, dest):
    """
    Instantiate an instance of the PM object for the image's package manager

    d -- the bitbake datastore
    dest -- the target / of any package manager operations
    """
    from oe.package_manager import RpmPM
    from oe.package_manager import OpkgPM
    from oe.package_manager import DpkgPM

    ptype = d.getVar('IMAGE_PKGTYPE', True)
    pm = None

    if ptype == 'rpm':
        pm = RpmPM(d, dest,
                   d.getVar('TARGET_VENDOR', True))
    elif ptype == 'ipk':
        pm = OpkgPM(d, dest,
                    d.getVar('IPKGCONF_TARGET', True),
                    d.getVar('ALL_MULTILIB_PACKAGE_ARCHS', True))
    elif ptype == 'deb':
        pm = DpkgPM(d, dest,
                    d.getVar('PACKAGE_ARCHS', True),
                    d.getVar('DPKG_ARCH', True))

    pm.write_index()
    pm.update()

    return pm
