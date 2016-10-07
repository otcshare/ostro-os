import subprocess
import shutil
from oe.package_manager import RpmPM
from oe.package_manager import OpkgPM
from oe.package_manager import DpkgPM
from oe.utils import format_pkg_list
from oe.rootfs import image_list_installed_packages
import oe.path
import swupd.path
import swupd.utils


def create_bundle_manifest(d, bundlename, dest=None):
    """
    create a bundle subscription receipt

    swupd-client expects a bundle subscription to exist for each
    installed bundle. This is simply an empty file named for the
    bundle in /usr/share/clear/bundles

    d -- the bitbake datastore
    bundlename -- the name of the bundle [and the receipt file name]
    dest -- the effective root location in which to create the receipt
        (default IMAGE_ROOTFS)
    """
    tgtpath = '/usr/share/clear/bundles'
    if dest:
        bundledir = dest + tgtpath
    else:
        bundledir = d.expand('${IMAGE_ROOTFS}%s' % tgtpath)
    bb.utils.mkdirhier(bundledir)
    open(os.path.join(bundledir, bundlename), 'w+b').close()


def get_bundle_packages(d, bundle):
    """
    Return a list of packages included in a bundle

    d -- the bitbake datastore
    bundle -- the name of the bundle for which we return a package list
    """
    pkgs = (d.getVarFlag('BUNDLE_CONTENTS', bundle, True) or '').split()
    return pkgs


def copy_core_contents(d):
    """
    Determine the os-core contents and copy the mega image to swupd's image directory.

    d -- the bitbake datastore
    """
    imagedir = d.expand('${SWUPDIMAGEDIR}/${OS_VERSION}')
    corefile = d.expand('${SWUPDIMAGEDIR}/${OS_VERSION}/os-core')
    contentsuffix = d.getVar('SWUPD_ROOTFS_MANIFEST_SUFFIX', True)
    imagesuffix = d.getVar('SWUPD_IMAGE_MANIFEST_SUFFIX', True)
    fullfile = d.expand('${SWUPDIMAGEDIR}/${OS_VERSION}/full')
    bundle = d.expand('${SWUPDIMAGEDIR}/${OS_VERSION}/full.tar')
    rootfs = d.getVar('IMAGE_ROOTFS', True)

    # Generate a manifest of the bundle content.
    bb.utils.mkdirhier(imagedir)
    unwanted_files = (d.getVar('SWUPD_FILE_BLACKLIST', True) or '').split()
    swupd.utils.create_content_manifests(rootfs,
                                         corefile + contentsuffix,
                                         corefile + imagesuffix,
                                         unwanted_files)

    havebundles = (d.getVar('SWUPD_BUNDLES', True) or '') != ''
    imgrootfs = d.getVar('MEGA_IMAGE_ROOTFS', True)
    if not havebundles:
        imgrootfs = rootfs
        for suffix in (contentsuffix, imagesuffix):
            shutil.copy2(corefile + suffix, fullfile + suffix)
    else:
        swupd.utils.create_content_manifests(imgrootfs,
                                             fullfile + contentsuffix,
                                             fullfile + imagesuffix,
                                             unwanted_files)
        manifest_files = swupd.utils.manifest_to_file_list(fullfile + contentsuffix) + \
                         swupd.utils.manifest_to_file_list(fullfile + imagesuffix)

    bb.debug(1, "Copying from image (%s) to full bundle (%s)" % (imgrootfs, bundle))
    # Create full.tar.gz instead of directory - speeds up
    # do_stage_swupd_input from ~11min in the Ostro CI to 6min.
    swupd.path.copyxattrfiles(d, manifest_files, imgrootfs, bundle, True)


def stage_image_bundle_contents(d, bundle):
    """
    Determine bundle contents which aren't part of os-core from the mega-image rootfs

    For an image-based bundle, generate a list of files which exist in the
    bundle but not os-core and stage those files from the mega image rootfs to
    the swupd inputs directory

    d -- the bitbake datastore
    bundle -- the name of the bundle to be staged
    """

    # Construct paths to manifest files and directories
    pn = d.getVar('PN', True)
    corefile = d.expand('${SWUPDIMAGEDIR}/${OS_VERSION}/os-core')
    bundlefile = d.expand('${SWUPDIMAGEDIR}/${OS_VERSION}/') + bundle
    contentsuffix = d.getVar('SWUPD_ROOTFS_MANIFEST_SUFFIX', True)
    imagesuffix = d.getVar('SWUPD_IMAGE_MANIFEST_SUFFIX', True)
    megarootfs = d.getVar('MEGA_IMAGE_ROOTFS', True)
    imagesrc = megarootfs.replace('mega', bundle)

    # Generate the manifest of the bundle image's file contents,
    # excluding blacklisted files and the content of the os-core.
    bb.debug(3, 'Writing bundle image file manifests %s' % bundlefile)
    unwanted_files = set((d.getVar('SWUPD_FILE_BLACKLIST', True) or '').split())
    unwanted_files.update(['/' + x for x in swupd.utils.manifest_to_file_list(corefile + contentsuffix)])
    swupd.utils.create_content_manifests(imagesrc,
                                         bundlefile + contentsuffix,
                                         bundlefile + imagesuffix,
                                         unwanted_files)

def stage_empty_bundle(d, bundle):
    """
    stage an empty bundle

    d -- the bitbake datastore
    bundle -- the name of the bundle to be staged
    """
    bundledir = d.expand('${SWUPDIMAGEDIR}/${OS_VERSION}/%s' % bundle)
    bb.utils.mkdirhier(bundledir)
    create_bundle_manifest(d, bundle, bundledir)


def copy_bundle_contents(d):
    """
    Stage bundle contents

    Copy the contents of all bundles from the mega image rootfs to the swupd
    inputs directory to ensure that any image postprocessing which modifies
    files is reflected in os-core bundle

    d -- the bitbake datastore
    """
    bb.debug(1, 'Copying contents of bundles for %s from mega image rootfs' % d.getVar('PN', True))
    bundles = (d.getVar('SWUPD_BUNDLES', True) or '').split()
    for bndl in bundles:
        stage_image_bundle_contents(d, bndl)
    bundles = (d.getVar('SWUPD_EMPTY_BUNDLES', True) or '').split()
    for bndl in bundles:
        stage_empty_bundle(d, bndl)
