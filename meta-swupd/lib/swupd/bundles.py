import subprocess
from oe.package_manager import RpmPM
from oe.package_manager import OpkgPM
from oe.package_manager import DpkgPM
from oe.utils import format_pkg_list
from oe.rootfs import image_list_installed_packages
import oe.path
import swupd.path
import swupd.utils


# swupd-client expects a bundle subscription to exist for each
# installed bundle. This is simply an empty file named for the
# bundle in /usr/share/clear/bundles
def create_bundle_manifest(d, bundlename, dest=None):
    tgtpath = '/usr/share/clear/bundles'
    if dest:
        bundledir = dest + tgtpath
    else:
        bundledir = d.expand('${IMAGE_ROOTFS}%s' % tgtpath)
    bb.utils.mkdirhier(bundledir)
    open(os.path.join(bundledir, bundlename), 'w+b').close()


def get_bundle_packages(d, bundle):
    pkgs = (d.getVarFlag('BUNDLE_CONTENTS', bundle, True) or '').split()
    return pkgs


# Copy the os-core contents from the mega image to swupd's image directory
def copy_core_contents(d):
    outfile = d.expand('${SWUPDIMAGEDIR}/${OS_VERSION}/${SWUPD_ROOTFS_MANIFEST}')
    bundledir = d.expand('${SWUPDIMAGEDIR}/${OS_VERSION}/${BUNDLE_NAME}/')
    rootfs = d.getVar('IMAGE_ROOTFS', True)

    # Generate a manifest of the bundle contents for pruning
    bb.utils.mkdirhier(bundledir)
    manifest_cmd = 'cd %s && find . ! -path . > %s' % (rootfs, outfile)
    subprocess.call(manifest_cmd, shell=True, stderr=subprocess.STDOUT)

    manifest_files = swupd.utils.manifest_to_file_list(outfile)
    bundle_file_contents = []
    # Don't copy files which should not be included in the swupd manifests
    unwanted_files = (d.getVar('SWUPD_FILE_BLACKLIST', True) or '').split()
    # The manifest files have a leading . before the /
    for f in manifest_files:
        if f[1:] not in unwanted_files:
            bundle_file_contents.append(f[2:])
    bb.debug(1, 'os-core contains %s items' % len(bundle_file_contents))
    bb.debug(1, "Copying from mega-image to os-core bundle dir (%s)" % (bundledir))
    swupd.path.copyxattrfiles(d, bundle_file_contents, d.getVar('MEGA_IMAGE_ROOTFS', True), bundledir)


# For each bundle we have already included their contents in the mega-image,
# thus we should be able to determine which packages were generated for that
# bundles features and contents through the generated dependency data. Thus:
# 1) determine the package manager and instantiate a PM object
# 2) collect a list of package names for each bundle
# 3) install the packages for the bundle into:
#        ${SWUPDIMAGEDIR}/${OS_VERSION}/$bndl
def stage_package_bundle_contents(d, bundle):
    bb.debug(1, 'Staging bundle contents for %s' % bundle)
    dest = d.expand("${SWUPDIMAGEDIR}/${OS_VERSION}/%s/" % bundle)
    pm = swupd.utils.get_package_manager(d, dest)

    pkgs = get_bundle_packages(d, bundle)
    pm.install(pkgs)
    # We don't want package manager artefacts left in the bundle 'chroot'
    pm.remove_packaging_data()
    # Remove any empty directories installed by the package manager, so as not
    # to pollute the 'chroot'
    swupd.path.remove_empty_directories(dest)

    # Create the swupd bundle manifest
    create_bundle_manifest(d, bundle, dest)

    # Generate a manifest of files in the bundle
    imagename = d.getVar('PN_BASE', True)
    if not imagename:
        imagename = d.getVar('IMAGE_BASENAME', True)
    manfile = d.expand("${SWUPDIMAGEDIR}/${OS_VERSION}/bundle-%s-%s${SWUPD_ROOTFS_MANIFEST_SUFFIX}") % (imagename, bundle)
    bb.debug(3, 'Writing bundle file manifest %s' % manfile)
    cmd = 'cd %s && find . ! -path . > %s' % (dest, manfile)
    oe.path.check_output(cmd, shell=True, stderr=subprocess.STDOUT)

    # Generate a manifest of packages in the bundle, we need this so that we
    # can compose a complete list of packages installed in any bundle images
    manfile = d.getVar('IMAGE_MANIFEST', True)
    manfile = manfile.replace(imagename, 'bundle-%s-%s' % (imagename, bundle))
    bb.debug(3, 'Writing bundle package manifest %s' % manfile)
    installed = image_list_installed_packages(d, dest)
    with open(manfile, 'w+') as manifest:
        manifest.write(format_pkg_list(installed, "ver"))
        manifest.write('\n')

    # Also write the manifest symlink
    if os.path.exists(manfile):
        dt = d.expand('-${DATETIME}.rootfs')
        manifest_link = manfile.replace(dt, '')
        if os.path.lexists(manifest_link):
            if d.getVar('RM_OLD_IMAGE', True) == "1" and \
                    os.path.exists(os.path.realpath(manifest_link)):
                os.remove(os.path.realpath(manifest_link))
            os.remove(manifest_link)
        bb.debug(3, 'Linking bundle package manifest from %s to %s' % (manfile, manifest_link))
        os.symlink(os.path.basename(manfile), manifest_link)


def recopy_package_bundle_contents(d, bundle):
    bb.debug(2, 'Re-copying files for package based bundle %s' % bundle)
    bundlecontents = []
    bundlebase = d.expand('${SWUPDIMAGEDIR}/${OS_VERSION}/')
    bundledir = bundlebase + bundle
    bb.debug(3, 'Scanning %s for bundle files' % bundledir)

    # Don't copy files which should not be included in the swupd manifests
    unwanted_files = (d.getVar('SWUPD_FILE_BLACKLIST', True) or '').split()
    def add_target_to_contents(root, file):
        # Compose a full path to the file
        tgt = os.path.join(root, file)
        # then strip out the prefix so it's just the target path
        tgt = tgt.replace(bundledir, '')
        if tgt not in unwanted_files:
            bundlecontents.append(tgt)

    for root, directories, files in os.walk(bundledir):
        for file in files:
            add_target_to_contents(root, file)
        for dir in directories:
            add_target_to_contents(root, dir)

    bundle_files = swupd.utils.sanitise_file_list(bundlecontents)

    # remove the current file contents of the bundle directory
    bb.debug(2, 'About to rm %s' % bundledir)
    oe.path.remove(bundledir)
    # copy over the required files from the megarootfs
    megarootfs = d.getVar('MEGA_IMAGE_ROOTFS', True)
    swupd.path.copyxattrfiles(d, bundle_files, megarootfs, bundledir)


# Copy bundle contents which aren't part of os-core from the mega-image rootfs
def copy_image_bundle_contents(d, bundle):
    bb.debug(2, 'Re-copying files for image based bundle %s' % bundle)

    # Construct paths to manifest files and directories
    pn = d.getVar('PN', True)
    manifest_path = d.expand('${SWUPDIMAGEDIR}/${OS_VERSION}/')
    base_manifest_name = d.getVar('SWUPD_ROOTFS_MANIFEST', True)
    image_manifest_name = base_manifest_name.replace(pn, 'bundle-%s-%s' % (pn, bundle))
    base_manifest = manifest_path + base_manifest_name
    image_manifest = manifest_path + image_manifest_name
    megarootfs = d.getVar('MEGA_IMAGE_ROOTFS', True)
    imagesrc = megarootfs.replace('mega', bundle)

    # Generate the manifest of the bundle image's file contents
    bb.debug(3, 'Writing bundle image file manifest %s' % image_manifest)
    cmd = 'cd %s && find . ! -path . > %s' % (imagesrc, image_manifest)
    oe.path.check_output(cmd, shell=True, stderr=subprocess.STDOUT)

    # Get a list of files in the bundle image which aren't in the base (os-core)
    bb.debug(3, 'Comparing manifest %s to %s' %(base_manifest, image_manifest))
    bundle_file_contents = swupd.utils.unique_contents(base_manifest, image_manifest)
    bb.debug(3, '%s has %s unique contents' % (bundle, len(bundle_file_contents)))

    bundle_files = swupd.utils.sanitise_file_list(bundle_file_contents)
    bb.debug(3, 'Sanitised file list for %s has %s contents' % (bundle, len(bundle_files)))

    # Finally, copy over the unique bundle contents
    bundledir = d.expand('${SWUPDIMAGEDIR}/${OS_VERSION}/%s/' % bundle)
    swupd.path.copyxattrfiles(d, bundle_files, megarootfs, bundledir)


def stage_empty_bundle(d, bundle):
    bundledir = d.expand('${SWUPDIMAGEDIR}/${OS_VERSION}/%s' % bundle)
    bb.utils.mkdirhier(bundledir)
    create_bundle_manifest(d, bundle, bundledir)


# Copy the staged bundle contents from the mega-image rootfs to ensure that
# any image postprocessing which modifies files is reflected in os-core bundle
def copy_bundle_contents(d):
    bb.debug(1, 'Recopying contents of bundles for %s from mega image rootfs' % d.getVar('PN', True))
    bundles = (d.getVar('SWUPD_BUNDLES', True) or '').split()
    for bndl in bundles:
        features = d.getVarFlag('BUNDLE_FEATURES', bndl, True)
        if features:
            copy_image_bundle_contents(d, bndl)
        else:
            stage_package_bundle_contents(d, bndl)
            recopy_package_bundle_contents(d, bndl)
    bundles = (d.getVar('SWUPD_EMPTY_BUNDLES', True) or '').split()
    for bndl in bundles:
        stage_empty_bundle(d, bndl)
