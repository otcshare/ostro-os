# Class for swupd integration -- generates input artefacts for consumption by
# swupd-server and calls swupd-server to process the inputs into update
# artefacts for consumption by swupd-client.
#
# Usage:
# * inherit this class in your core OS image. swupd-based OS's use bundles, the
#   primary one of which, os-core, is defined as the contents of this image.
# * Assign a list of names for bundles you wish to generate to the
#   SWUPD_BUNDLES variable i.e. SWUPD_BUNDLES = "feature_one feature_two"
# * Assign a list of packages for which their content should be included in
#   a bundle to a varflag of BUNDLE_CONTENTS which matches the bundle name
#   i.e. BUNDLE_CONTENTS[feature_one] = "package_one package_three package_six"
# * Ensure the OS_VERSION variable is assigned an integer value and increased
#   before each image build which should generate swupd update artefacts.
#
# See docs/Guide.md for more information.

DEPLOY_DIR_SWUPDBASE = "${DEPLOY_DIR}/swupd/${MACHINE}"
SWUPD_ROOTFS_MANIFEST_SUFFIX = "-files-in-image.txt"
SWUPD_ROOTFS_MANIFEST = "${PN}${SWUPD_ROOTFS_MANIFEST_SUFFIX}"

# User configurable variables to disable all swupd processing or deltapack
# generation.
SWUPD_GENERATE ??= "1"
SWUPD_DELTAPACKS ??= "1"
# Create delta packs for N versions back — default 2
SWUPD_N_DELTAPACK ??= "2"

SWUPD_LOG_FN ??= "bbdebug 1"

# This version number *must* map to VERSION_ID in /etc/os-release and *must* be
# a non-negative integer that fits in an int.
OS_VERSION ??= "${DISTRO_VERSION}"

IMAGE_INSTALL_append = " swupd-client os-release"

# We need to preserve xattrs which is only supported by GNU tar >= 1.27
# to be sure this functionality works as expected use the tar-replacement-native
DEPENDS += "tar-replacement-native"
EXTRANATIVEPATH += "tar-native"

inherit distro_features_check
REQUIRED_DISTRO_FEATURES = "systemd"

python () {
    if d.getVar('VIRTUAL-RUNTIME_init_manager', True) != 'systemd':
        bb.error('swupd integration requires the systemd init manager')

    ver = d.getVar('OS_VERSION', True) or 'invalid'
    try:
        int(ver)
    except ValueError:
        bb.fatal("Invalid value for OS_VERSION (%s), must be a non-negative integer value." % ver)

    havebundles = (d.getVar('SWUPD_BUNDLES', True) or '') != ''

    pn_base = d.getVar('PN_BASE', True)
    pn = d.getVar('PN', True)

    # We set the path to the rootfs folder of the mega image here so that
    # it's simple to refer to later.
    megarootfs = d.getVar('IMAGE_ROOTFS', True)
    if havebundles:
        megarootfs = megarootfs.replace('/' + pn +'/', '/bundle-%s-mega/' % (pn_base or pn))
        d.setVar('MEGA_IMAGE_ROOTFS', megarootfs)

    if pn_base is not None:
        # We want all virtual images from this recipe to deploy to the same
        # directory
        deploy_dir = d.getVar('DEPLOY_DIR_SWUPDBASE', True)
        deploy_dir = os.path.join(deploy_dir, pn_base)
        d.setVar('DEPLOY_DIR_SWUPD', deploy_dir)

        # We need all virtual images from this recipe to share the same pseudo
        # database so that permissions are correctly set in the copied bundle
        # directories when swupd post-processing happens.
        #
        # Because real image building via SWUPD_IMAGES can happen also after
        # the initial "bitbake <core image>" invocation, we have to keep that
        # pseudo database around and cannot delete it.
        pseudo_state = d.expand('${TMPDIR}/work-shared/${PN_BASE}/pseudo')
        d.setVar('PSEUDO_LOCALSTATEDIR', pseudo_state)

        # Non mega virtual images must depend on the mega image having been
        # built, as they will copy contents from there
        if d.getVar('BUNDLE_NAME', True) == 'mega':
            return

        mega_name = (' bundle-%s-mega:do_image_complete' % pn_base)
        d.appendVarFlag('do_image', 'depends', mega_name)

        return

    # We use a shared Pseudo database in order to ensure that all tasks have
    # full awareness of the files created for the base image recipe and each
    # of its virtual recipes (primarily the mega image).
    # However, we must be careful with the pseudo database and managing
    # database lifecycles in order to avoid confusion should inode numbers be
    # reused when files are deleted outside of pseudo's awareness.
    pseudo_state = d.expand('${TMPDIR}/work-shared/${IMAGE_BASENAME}/pseudo')
    d.setVar('PSEUDO_LOCALSTATEDIR', pseudo_state)

    deploy_dir = d.expand('${DEPLOY_DIR_SWUPDBASE}/${IMAGE_BASENAME}')
    d.setVar('DEPLOY_DIR_SWUPD', deploy_dir)
    # do_stage_bundle_contents requires ${DEPLOY_DIR_SWUPD}/image/${OS_VERSION}
    varflags = '%s/image/%s' % (deploy_dir, ver)
    d.setVarFlag('do_stage_bundle_contents', 'dirs', varflags)
    # do_swupd_update requires the full swupd directory hierarchy
    varflags = '%s/image %s/empty %s/www %s' % (deploy_dir, deploy_dir, deploy_dir, deploy_dir)
    d.setVarFlag('do_swupd_update', 'dirs', varflags)

    # For the base image only, set the BUNDLE_NAME to os-core and generate the
    # virtual image for the mega image
    d.setVar('BUNDLE_NAME', 'os-core')

    bundles = (d.getVar('SWUPD_BUNDLES', True) or "").split()
    extended = (d.getVar('BBCLASSEXTEND', True) or "").split()

    # We need to prevent the user defining bundles where the name might clash
    # with naming in meta-swupd and swupd itself:
    #  * mega is the name of our super image, an implementation detail in
    #     meta-swupd
    #  * full is the name used by swupd for the super manifest (listing all
    #     files in all bundles of the OS)
    def check_reserved_name(name):
        reserved_bundles = ['mega', 'full']
        if name in reserved_bundles:
            bb.error('SWUPD_BUNDLES contains an item named "%s", this is a reserved name. Please rename that bundle.' % name)

    for bndl in bundles:
        check_reserved_name(bndl)

    if havebundles:
        extended.append('swupdbundle:mega')

    # Generate real image files from the os-core bundle plus
    # certain additional bundles. All of these images can share
    # the same swupd update stream, the only difference is the
    # number of pre-installed bundles.
    for imageext in (d.getVar('SWUPD_IMAGES', True) or '').split():
        extended.append('swupdimage:%s' % imageext)

    d.setVar('BBCLASSEXTEND', ' '.join(extended))

    # The base image should depend on the mega-image having been populated
    # to ensure that we're staging the same shared files from the sysroot as
    # the bundle images.
    if havebundles:
        mega_name = (' bundle-%s-mega:do_image_complete' % pn)
        d.appendVarFlag('do_image', 'depends', mega_name)
        d.appendVarFlag('do_stage_swupd_inputs', 'depends', mega_name)
}

def copyxattrtree(src, dst):
    import subprocess

    bb.utils.mkdirhier(dst)
    # tar does not properly copy xattrs when used like this.
    # See the comment on tar in meta/classes/image_types.bbclass
    cmd = "tar --xattrs --xattrs-include='*' -cf - -C %s -p . | tar -p --xattrs --xattrs-include='*' -xf - -C %s" % (src, dst)
    oe.path.check_output(cmd, shell=True, stderr=subprocess.STDOUT)

def copyxattrfiles(d, filelist, src, dst):
    import subprocess

    def pathtostring(path):
        return path.replace('/', '-')

    bb.debug(4, 'Copying xattr files from %s to %s' % (src, dst))
    bb.utils.mkdirhier(dst)
    files = sorted(filelist)

    copyfile = '%s/copyxattrfiles-%s-%s.txt' % (d.getVar('WORKDIR', True), pathtostring(src), pathtostring(dst))
    if os.path.exists(copyfile):
        os.remove(copyfile)
    with open(copyfile, 'w') as fdest:
        fdest.write('-C%s\n' % src)
        for f in files:
            fdest.write('%s\n' % f)

    cmd = "tar --xattrs --xattrs-include='*' --no-recursion -cf - -T %s -p | tar -p --xattrs --xattrs-include='*' -xf - -C %s" % (copyfile, dst)
    oe.path.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    os.remove(copyfile)

# swupd-client expects a bundle subscription to exist for each
# installed bundle. This is simply an empty file named for the
# bundle in /usr/share/clear/bundles
def create_bundle_manifest(d, bundlename):
    bundledir = d.expand('${IMAGE_ROOTFS}/usr/share/clear/bundles')
    bb.utils.mkdirhier(bundledir)
    open(os.path.join(bundledir, bundlename), 'w+b').close()

fakeroot do_rootfs_append () {
    bundle = d.getVar('BUNDLE_NAME', True)
    bundles = ['os-core']
    if bundle == 'mega':
        bundles.extend((d.getVar('SWUPD_BUNDLES', True) or '').split())
    else:
        bundles.append(bundle)
    # swupd-client expects a bundle subscription to exist for each
    # installed bundle. This is simply an empty file named for the
    # bundle in /usr/share/clear/bundles
    for bundle in bundles:
        create_bundle_manifest(d, bundle)
}

def swupd_create_rootfs(d):
    # Create or replace the do_image rootfs output with the corresponding
    # subset from the mega rootfs. Done even if there is no actual image
    # getting produced, because there may be QA tests defined for
    # do_image which depend on seeing the actual rootfs that would be
    # used for images.
    bndl = d.getVar('BUNDLE_NAME', True)
    pn = d.getVar('PN', True)
    pn_base = d.getVar('PN_BASE', True)
    imageext = d.getVar('IMAGE_BUNDLE_NAME', True) or ''
    if bndl and bndl != 'os-core':
        bb.debug(2, "Skipping swupd_create_rootfs() in bundle image %s for bundle %s." % (pn, bndl))
        return

    # Sanity checking was already done in swupdimage.bbclass.
    # Here we can simply use the settings.
    imagebundles = d.getVarFlag('SWUPD_IMAGES', imageext, True).split() if imageext else []
    rootfs = d.getVar('IMAGE_ROOTFS', True)
    rootfs_contents = []
    if not pn_base: # the base image
        import subprocess

        # For the base image only we need to remove all of the files that were
        # installed during the base do_rootfs and replace them with the
        # equivalent files from the mega image.
        #
        # The virtual image recipes will already have an empty rootfs.
        outfile = d.expand('${WORKDIR}/orig-rootfs-manifest.txt')
        rootfs = d.getVar('IMAGE_ROOTFS', True)
        # Generate a manifest of the current file contents
        manifest_cmd = 'cd %s && find . ! -path . > %s' % (rootfs, outfile)
        subprocess.call(manifest_cmd, shell=True, stderr=subprocess.STDOUT)
        # Remove the current rootfs contents
        oe.path.remove('%s/*' % rootfs)
        for entry in manifest_to_file_list(outfile):
            rootfs_contents.append(entry[1:])
        # clean up
        os.unlink(outfile)
    else: # non-base image, i.e. swupdimage
        manifest = d.expand("${DEPLOY_DIR_SWUPD}/image/${OS_VERSION}/${PN_BASE}${SWUPD_ROOTFS_MANIFEST_SUFFIX}")
        for entry in manifest_to_file_list(manifest):
            rootfs_contents.append(entry[1:])

    bb.debug(3, 'rootfs_contents has %s entries' % (len(rootfs_contents)))
    # TODO: replace with a call to copyxattrfiles()
    # Copy all files from the mega bundle...
    copyxattrtree(d.getVar('MEGA_IMAGE_ROOTFS', True), rootfs)

    # ... and then remove files again which shouldn't have been copied.
    for bundle in imagebundles:
        manifest = d.expand("${DEPLOY_DIR_SWUPD}/image/${OS_VERSION}/bundle-${PN_BASE}-%s${SWUPD_ROOTFS_MANIFEST_SUFFIX}") % bundle
        for entry in manifest_to_file_list(manifest):
            rootfs_contents.append(entry[1:])

    # Prune the items not in the manifest
    bb.debug(3, 'Desired content of rootfs:\n' + '\n'.join(rootfs_contents))
    remove_unlisted_files_from_directory(rootfs_contents, rootfs)

    # Create .rootfs.manifest for bundle images as the union of all
    # contained bundles. Otherwise the image wouldn't have that file,
    # which breaks certain image types ("toflash" in the Edison BSP)
    # and utility classes (like isafw.bbclass).
    if imageext:
        packages = set()
        manifest = d.getVar('IMAGE_MANIFEST', True)
        for bundle in imagebundles:
            bundlemanifest = manifest.replace(pn, 'bundle-%s-%s' % (pn_base, bundle))
            with open(bundlemanifest) as f:
                 packages.update(f.readlines())
        with open(manifest, 'w') as f:
            f.writelines(sorted(packages))

do_image_append () {
    swupd_create_rootfs(d)
}

SWUPDIMAGEDIR = "${WORKDIR}/swupd-image"
# Copy the os-core contents from the mega image to swupd's image directory
def copy_core_contents(d):
    import subprocess

    outfile = d.expand('${SWUPDIMAGEDIR}/${OS_VERSION}/${SWUPD_ROOTFS_MANIFEST}')
    bundledir = d.expand('${SWUPDIMAGEDIR}/${OS_VERSION}/${BUNDLE_NAME}/')
    rootfs = d.getVar('IMAGE_ROOTFS', True)

    # Generate a manifest of the bundle contents for pruning
    bb.utils.mkdirhier(bundledir)
    manifest_cmd = 'cd %s && find . ! -path . > %s' % (rootfs, outfile)
    subprocess.call(manifest_cmd, shell=True, stderr=subprocess.STDOUT)

    manifest_files = manifest_to_file_list(outfile)
    bundle_file_contents = []
    # The manifest files have a leading . before the /
    for f in manifest_files:
        bundle_file_contents.append(f[2:])
    bb.debug(1, 'os-core has %s unique contents' % len(bundle_file_contents))
    bb.debug(1, "Copying from mega-image to os-core bundle dir (%s)" % (bundledir))
    copyxattrfiles(d, bundle_file_contents, d.getVar('MEGA_IMAGE_ROOTFS', True), bundledir)

# Instantiate an instance of the PM object for the image's package manager
def get_package_manager(d, dest):
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

    return pm

def get_bundle_packages(d, bundle):
    pkgs = (d.getVarFlag('BUNDLE_CONTENTS', bundle, True) or '').split()
    return pkgs

# For each bundle we have already included their contents in the mega-image,
# thus we should be able to determine which packages were generated for that
# bundles features and contents through the generated dependency data. Thus:
# 1) determine the package manager and instantiate a PM object
# 2) collect a list of package names for each bundle
# 3) install the packages for the bundle into:
#        ${SWUPDIMAGEDIR}/${OS_VERSION}/$bndl
def stage_bundle_contents(d):
    from oe.package_manager import RpmPM
    from oe.package_manager import OpkgPM
    from oe.package_manager import DpkgPM
    from oe.utils import format_pkg_list
    from oe.rootfs import image_list_installed_packages
    import subprocess

    bb.debug(1, 'Staging bundle contents for %s' % d.getVar('PN', True))
    basedest = d.expand("${SWUPDIMAGEDIR}/${OS_VERSION}/")
    bundles = (d.getVar('SWUPD_BUNDLES', True) or '').split()
    for bndl in bundles:
        bb.debug(1, 'Staging bundle contents for %s' % bndl)
        dest = basedest + bndl
        pm = get_package_manager(d, dest)

        pm.update()
        pkgs = get_bundle_packages(d, bndl)
        pm.install(pkgs)

        # Generate a manifest of files in the bundle
        imagename = d.getVar('PN_BASE', True)
        if not imagename:
            imagename = d.getVar('IMAGE_BASENAME', True)
        manfile = d.expand("${SWUPDIMAGEDIR}/${OS_VERSION}/bundle-%s-%s${SWUPD_ROOTFS_MANIFEST_SUFFIX}") % (imagename, bndl)
        bb.debug(3, 'Writing bundle file manifest %s' % manfile)
        cmd = 'cd %s && find . ! -path . > %s' % (dest, manfile)
        oe.path.check_output(cmd, shell=True, stderr=subprocess.STDOUT)

        # Generate a manifest of packages in the bundle, we need this so that we
        # can compose a complete list of packages installed in any bundle images
        manfile = d.getVar('IMAGE_MANIFEST', True)
        manfile = manfile.replace(imagename, 'bundle-%s-%s' % (imagename, bndl))
        bb.debug(3, 'Writing bundle package manifest %s' % manfile)
        installed = image_list_installed_packages(d, dest)
        with open(manfile, 'w+') as manifest:
            manifest.write(format_pkg_list(installed, "ver"))
            manifest.write('\n')

        # We don't want package manager artefacts left in the bundle 'chroot'
        pm.remove_packaging_data()

# Recopy the staged bundle contents from the mega-image rootfs to ensure that
# any image postprocessing which modifies files is reflected in os-core bundle
def recopy_bundle_contents(d):
    import subprocess

    bb.debug(1, 'Recopying contents of bundles for %s from mega image rootfs' % d.getVar('PN', True))
    bundles = (d.getVar('SWUPD_BUNDLES', True) or '').split()
    for bndl in bundles:
        bb.debug(2, 'Re-copying files for %s' % bndl)
        bundlecontents = set()
        bundlebase = d.expand('${SWUPDIMAGEDIR}/${OS_VERSION}/')
        bundledir = bundlebase + bndl
        bb.debug(3, 'Scanning %s for bundle files' % bundledir)

        def add_target_to_contents(root, file):
            # Compose a full path to the file
            tgt = os.path.join(root, file)
            # then strip out the prefix so it's just the target path
            tgt = tgt.replace(bundledir, '')
            bundlecontents.add(tgt[1:])

        for root, directories, files in os.walk(bundledir):
            for file in files:
                add_target_to_contents(root, file)
            for dir in directories:
                add_target_to_contents(root, dir)

        # Also copy the bundles swupd bundle manifest and its parent hierarchy
        bndlman = 'usr/share/clear/bundles/' + bndl
        bundlecontents.add('usr/share/clear')
        bundlecontents.add('usr/share/clear/bundles')
        bundlecontents.add(bndlman)
        # remove the current file contents of the bundle directory
        bb.debug(2, 'About to rm %s' % bundledir)
        oe.path.remove(bundledir)
        # copy over the required files from the megarootfs
        megarootfs = d.getVar('MEGA_IMAGE_ROOTFS', True)
        copyxattrfiles(d, list(bundlecontents), megarootfs, bundledir)

fakeroot python do_stage_swupd_inputs () {
    if d.getVar('PN_BASE', True):
        bb.debug(2, 'Skipping update input staging for non-base image %s' % d.getVar('PN', True))
        return

    copy_core_contents(d)
    stage_bundle_contents(d)
    recopy_bundle_contents(d)
}
addtask stage_swupd_inputs after do_image before do_swupd_update

SSTATETASKS += "do_stage_swupd_inputs"
do_stage_swupd_inputs[sstate-inputdirs] = "${SWUPDIMAGEDIR}"
do_stage_swupd_inputs[sstate-outputdirs] = "${DEPLOY_DIR_SWUPD}/image/"

python do_stage_swupd_inputs_setscene () {
    sstate_setscene(d)
}
addtask do_stage_swupd_inputs_setscene
do_stage_swupd_inputs_setscene[dirs] = "${SWUPDIMAGEDIR} ${DEPLOY_DIR_SWUPD}/image/"

# Generate a list of files which exist in the bundle image, but not the base
# image.
def delta_contents(difflist):
    # '- ' - line unique to lhs
    # '+ ' - line unique to rhs
    # '  ' - line common
    # '? ' - line not present in either
    #
    # difflist should be a list containing the output of difflib.Differ.compare
    #       where the lhs (left-hand-side) was the base image and the rhs
    #       (right-hand-side) was base image + extras (the bundle image).
    #
    # returns a list containing the items which are unique in the rhs
    cont = []
    for ln in difflist:
        if ln[0] == '+':
            cont.append(ln[3:])
    return cont

# Open a manifest file and read it into a list
def manifest_to_file_list(manifest_fn):
    image_manifest_list = []
    with open(manifest_fn) as image:
        image_manifest_list = image.read().splitlines()

    return image_manifest_list

# Compare the bundle image manifest to the base image manifest and return
# a list of files unique to the bundle image.
def unique_contents(base_manifest_fn, image_manifest_fn):
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

# Takes a list of files and a base directory, removes items from the base
# directory which don't exist in the list
def remove_unlisted_files_from_directory (file_list, directory, fullprune=False):
    for root, dirs, files in os.walk(directory):
        replace = '/'
        if not directory.endswith('/'):
            replace = ''
        relroot = root.replace(directory, replace)
        #bb.debug(1, 'Substituting "%s" for %s in root of %s to give %s' % (replace, directory, root, relroot))
        # Beware that os.walk() treats symlinks to directories like directories.
        # We need to treat them like files because they get removed with os.remove().
        for f in files:
            fpath = os.path.join(relroot, f)
            if fpath not in file_list:
                fpath_absolute = os.path.join(root, f)
                bb.debug(3, 'Pruning %s from the bundle (%s)' % (fpath, fpath_absolute))
                os.remove(fpath_absolute)
        for d in dirs:
            dpath = os.path.join(relroot, d)
            dpath_absolute = os.path.join(root, d)
            if os.path.islink(dpath_absolute) and dpath not in file_list:
                bb.debug(3, 'Pruning %s from the bundle (%s)' % (dpath, dpath_absolute))
                os.remove(dpath_absolute)

    # Now need to clean up empty directories, unless they were listed in the
    # the bundle's manifest
    for dir, _, _ in os.walk(directory, topdown=False):
        replace = '/'
        if not directory.endswith('/'):
            replace = ''
        d = dir.replace(directory, replace)
        bb.debug(3, 'Checking whether to delete %s (%s)' % (d, dir))
        if fullprune or (d not in file_list):
            try:
                bb.debug(3, 'Attempting to remove unwanted directory %s (%s)' % (d, dir))
                os.rmdir(dir)
            except OSError as err:
                bb.debug(2, 'Not removing %s, reason: %s' % (dir, err.strerror))
        else:
            bb.debug(3, 'Not removing wanted empty directory %s' % d)

SWUPD_FORMAT ??= "3"
fakeroot do_swupd_update () {
    if [ -z "${BUNDLE_NAME}" ] || [ ! -z "${PN_BASE}" ] ; then
        bbwarn 'We only generate swupd updates for the base image, skipping ${PN}:do_swupd_update'
        exit
    fi

    if [ ! "${SWUPD_GENERATE}" -eq 1 ]; then
        bbnote 'Update generation disabled, skipping.'
        exit
    fi

    export SWUPD_CERTS_DIR="${STAGING_ETCDIR_NATIVE}/swupd-certs"
    export LEAF_KEY="leaf.key.pem"
    export LEAF_CERT="leaf.cert.pem"
    export CA_CHAIN_CERT="ca-chain.cert.pem"
    export PASSPHRASE="${SWUPD_CERTS_DIR}/passphrase"

    export XZ_DEFAULTS="--threads 0"

    ${SWUPD_LOG_FN} "New OS_VERSION is ${OS_VERSION}"
    # If the swupd directory already exists don't trample over it, but let
    # the user know we're not doing any update generation.
    if [ -e ${DEPLOY_DIR_SWUPD}/www/${OS_VERSION} ]; then
        bbwarn 'swupd image directory exists for OS_VERSION=${OS_VERSION}, not generating updates.'
        bbwarn 'Ensure OS_VERSION is incremented if you want to generate updates.'
        exit
    fi

    # Generate swupd-server configuration
    bbdebug 2 "Writing ${DEPLOY_DIR_SWUPD}/server.ini"
    if [ -e "${DEPLOY_DIR_SWUPD}/server.ini" ]; then
       rm ${DEPLOY_DIR_SWUPD}/server.ini
    fi
    cat << END > ${DEPLOY_DIR_SWUPD}/server.ini
[Server]
imagebase=${DEPLOY_DIR_SWUPD}/image/
outputdir=${DEPLOY_DIR_SWUPD}/www/
emptydir=${DEPLOY_DIR_SWUPD}/empty/
END

    if [ -e ${DEPLOY_DIR_SWUPD}/image/latest.version ]; then
        PREVREL=`cat ${DEPLOY_DIR_SWUPD}/image/latest.version`
    else
        bbdebug 2 "Stubbing out empty latest.version file"
        touch ${DEPLOY_DIR_SWUPD}/image/latest.version
        PREVREL="0"
    fi

    GROUPS_INI="${DEPLOY_DIR_SWUPD}/groups.ini"
    bbdebug 2 "Writing ${GROUPS_INI}"
    if [ -e "${DEPLOY_DIR_SWUPD}/groups.ini" ]; then
       rm ${DEPLOY_DIR_SWUPD}/groups.ini
    fi
    touch ${GROUPS_INI}
    ALL_BUNDLES="os-core ${SWUPD_BUNDLES}"
    for bndl in ${ALL_BUNDLES}; do
        echo "[$bndl]" >> ${GROUPS_INI}
        echo "group=$bndl" >> ${GROUPS_INI}
        echo "" >> ${GROUPS_INI}
    done

    ${SWUPD_LOG_FN} "Generating update from $PREVREL to ${OS_VERSION}"
    ${STAGING_BINDIR_NATIVE}/swupd_create_update -S ${DEPLOY_DIR_SWUPD} --osversion ${OS_VERSION} --format ${SWUPD_FORMAT}

    ${SWUPD_LOG_FN} "Generating fullfiles for ${OS_VERSION}"
    ${STAGING_BINDIR_NATIVE}/swupd_make_fullfiles -S ${DEPLOY_DIR_SWUPD} ${OS_VERSION}

    ${SWUPD_LOG_FN} "Generating zero packs, this can take some time."
    for bndl in ${ALL_BUNDLES}; do
        ${SWUPD_LOG_FN} "Generating zero pack for $bndl"
        ${STAGING_BINDIR_NATIVE}/swupd_make_pack -S ${DEPLOY_DIR_SWUPD} 0 ${OS_VERSION} $bndl
    done

    # Generate delta-packs going back SWUPD_N_DELTAPACK versions
    if [ ${SWUPD_DELTAPACKS} -eq 1 -a ${SWUPD_N_DELTAPACK} -gt 0 -a $PREVREL -gt 0 ]; then
        bundles="os-core ${SWUPD_BUNDLES}"
        for bndl in $bundles; do
            bndlcnt=0
            # Build list of previous versions and pick the last n ones to build
            # deltas against. Ignore the latest one, which is the one we build
            # right now.
            ls -d -1 ${DEPLOY_DIR_SWUPD}/image/*/$bndl | sed -e 's;${DEPLOY_DIR_SWUPD}/image/\([^/]*\)/.*;\1;' | grep -e '^[0-9]*$' | sort -n | head -n -1 | tail -n ${SWUPD_N_DELTAPACK} | while read prevver; do
                ${SWUPD_LOG_FN} "Generating delta pack from $prevver to ${OS_VERSION} for $bndl"
                ${STAGING_BINDIR_NATIVE}/swupd_make_pack -S ${DEPLOY_DIR_SWUPD} $prevver ${OS_VERSION} $bndl
            done
        done
    fi

    # Write version to www/version/format${SWUPD_FORMAT}/latest and image/latest.version
    bbdebug 2 "Writing latest file"
    mkdir -p ${DEPLOY_DIR_SWUPD}/www/version/format${SWUPD_FORMAT}
    echo ${OS_VERSION} > ${DEPLOY_DIR_SWUPD}/www/version/format${SWUPD_FORMAT}/latest
    echo ${OS_VERSION} > ${DEPLOY_DIR_SWUPD}/image/latest.version
}

SWUPDDEPENDS = "\
    virtual/fakeroot-native:do_populate_sysroot \
    rsync-native:do_populate_sysroot \
    bsdiff-native:do_populate_sysroot \
    swupd-server-native:do_populate_sysroot \
"
addtask swupd_update after do_image_complete do_recopy_bundle_contents before do_build
do_swupd_update[depends] = "${SWUPDDEPENDS}"

# pseudo does not handle xattrs correctly for hardlinks:
# https://bugzilla.yoctoproject.org/show_bug.cgi?id=9317
#
# This started to become a problem when copying rootfs
# content around for swupd bundle creation. As a workaround,
# we avoid having hardlinks in the rootfs and replace them
# with symlinks.
python swupd_replace_hardlinks () {
    import os
    import stat

    # Collect all inodes and which entries share them.
    inodes = {}
    for root, dirs, files in os.walk(d.getVar('IMAGE_ROOTFS', True)):
        for file in files:
            path = os.path.join(root, file)
            s = os.lstat(path)
            if stat.S_ISREG(s.st_mode):
                inodes.setdefault(s.st_ino, []).append(path)

    for inode, paths in inodes.iteritems():
        if len(paths) > 1:
            paths.sort()
            bb.debug(3, 'Removing hardlinks: %s' % ' = '.join(paths))
            # Arbitrarily pick the first entry as symlink target.
            target = paths.pop(0)
            for path in paths:
                reltarget = os.path.relpath(target, os.path.dirname(path))
                os.unlink(path)
                os.symlink(reltarget, path)
}
ROOTFS_POSTPROCESS_COMMAND += "swupd_replace_hardlinks; "

# swupd-client checks VERSION_ID, which must match the OS_VERSION
# used for generating swupd bundles in the current build.
#
# We patch this during image creation and exclude OS_VERSION from the
# dependencies because doing it during the compilation of os-release.bb
# would trigger a rebuild even if all that changed is the OS_VERSION.
# It would also affect builds of images where swupd is not active. Both
# is undesirable.
#
# If triggering a rebuild on each OS_VERSION change is desired,
# then this can be achieved by influencing the os-release package
# by setting in local.conf:
# VERSION_ID = "${OS_VERSION}"

swupd_patch_os_release () {
    sed -i -e 's/^VERSION_ID *=.*/VERSION_ID="${OS_VERSION}"/' ${IMAGE_ROOTFS}/usr/lib/os-release
}
swupd_patch_os_release[vardepsexclude] = "OS_VERSION"
ROOTFS_POSTPROCESS_COMMAND += "swupd_patch_os_release; "

SWUPD_IMAGE_SANITY_CHECKS ??= ""
# Add image-level QA/sanity checks to SWUPD_IMAGE_SANITY_CHECKS
#
# SWUPD_IMAGE_SANITY_CHECKS += " \
#     swupd_check_dangling_symlinks \
# "

# This task runs all functions in SWUPD_IMAGE_SANITY_CHECKS after the image
# construction has completed in order to validate the resulting image.
# Image sanity checks should raise a NotImplementedError when they fail,
# passing any failure messages to the Exception. For example:
#
#    python swupd_image_check_always_fails () {
#        raise NotImplementedError('This check always fails')
#    }
python do_swupd_sanity_check_image () {
    funcs = (d.getVar('SWUPD_IMAGE_SANITY_CHECKS', True) or '').split()
    qasane = True

    for func in funcs:
        try:
            bb.build.exec_func(func, d, pythonexception=True)
        except NotImplementedError as e:
            qasane = False
            bb.error(str(e))

    if not qasane:
        bb.fatal('QA errors found whilst checking swupd image sanity.')
}
addtask swupd_sanity_check_image after do_image_complete before do_build

# Check whether the constructed image contains any dangling symlinks, these
# are likely to indicate deeper issues.
# NOTE: you'll almost certainly want to override these for your distro.
# /run, /var/volatile and /dev only get mounted at runtime.
SWUPD_IMAGE_SYMLINK_WHITELIST ??= " \
    /run/lock \
    /var/volatile/tmp \
    /var/volatile/log \
    /dev/null \
    /proc/mounts \
    /run/resolv.conf \
"

python swupd_check_dangling_symlinks() {
    rootfs = d.getVar("IMAGE_ROOTFS", True)

    def resolve_links(target, root):
        if not target.startswith('/'):
            target = os.path.normpath(os.path.join(root, target))
        else:
            # Absolute links are in fact relative to the rootfs.
            # Can't use os.path.join() here, it skips the
            # components before absolute paths.
            target = os.path.normpath(rootfs + target)
        if os.path.islink(target):
            root = os.path.dirname(target)
            target = os.readlink(target)
            target = resolve_links(target, root)
        return target

    # Check for dangling symlinks. One common reason for them
    # in swupd images is update-alternatives where the alternative
    # that gets chosen in the mega image then is not installed
    # in a sub-image.
    #
    # Some allowed cases are whitelisted.
    whitelist = d.getVar('SWUPD_IMAGE_SYMLINK_WHITELIST', True).split()
    message = ''
    for root, dirs, files in os.walk(rootfs):
        for entry in files + dirs:
            path = os.path.join(root, entry)
            if os.path.islink(path):
                target = os.readlink(path)
                final_target = resolve_links(target, root)
                if not os.path.exists(final_target) and not final_target[len(rootfs):] in whitelist:
                    message = message + 'Dangling symlink: %s -> %s -> %s does not resolve to a valid filesystem entry.\n' % (path, target, final_target)

    if message != '':
        message = message + '\nIf these symlinks not pointing to a valid destination is not an issue \
i.e. the link is to a file which only exists at runtime, such as files in /proc, add them to \
SWUPD_IMAGE_SYMLINK_WHITELIST to resolve this error.'
        raise NotImplementedError(message)
}
