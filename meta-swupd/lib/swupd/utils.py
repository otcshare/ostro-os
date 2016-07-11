

def sanitise_file_list(filelist):
    """
    expand a list of paths ensuring each component is represented in the list

    We need to ensure that each component of every file path to be copied is
    present in the list.
    This is because when copying the file contents using copyxattrfiles() any
    intermediate path components which aren't explicitly specified will be
    automatically created (instead of being copied) and thus end up with the
    default permissions for newly created directories -- this will likely lead
    to hash mismatches in the swupd Manifests and verification failures.
    We also take the step of removing a leading / from the path, as required
    by copyxattrfiles()

    filelist -- the list of files to expand
    """
    sanitised = set()
    rootrepr = ['', '.', '/']

    def addpathcomponents(path):
        """
        add each component of path to the file list

        path -- the path to add compoents from
        """
        dirname = os.path.dirname(path)
        while dirname:
            # If the directory is a representation of / then we're done
            if dirname in rootrepr:
                break
            sanitised.add(dirname[1:])
            # Process the next component of the path
            dirname = os.path.dirname(dirname)

    for f in filelist:
        # Ensure every component of the path is included in the file list
        addpathcomponents(f)
        # Remove / prefix for passing to tar
        sanitised.add(f[1:])

    return sorted(sanitised)


def manifest_to_file_list(manifest_fn):
    """
    open a manifest file and read it into a list

    manifest_fn -- the manifest file to read
    """
    image_manifest_list = []
    with open(manifest_fn) as image:
        image_manifest_list = image.read().splitlines()

    return image_manifest_list


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
