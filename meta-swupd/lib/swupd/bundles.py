import glob
import re
import subprocess
import shutil
import urllib.request
import urllib.error
from bb.utils import export_proxies
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

    # Create full.tar.gz instead of directory - speeds up
    # do_stage_swupd_input from ~11min in the Ostro CI to 6min.
    # Where we take the data from depends on whether we have bundles:
    # without them, there's also no "mega" bundle and we work
    # directly with the rootfs of the main image recipe.
    havebundles = (d.getVar('SWUPD_BUNDLES', True) or '') != ''
    if not havebundles:
        for suffix in (contentsuffix, imagesuffix):
            shutil.copy2(corefile + suffix, fullfile + suffix)
        bb.debug(1, "Copying from image rootfs (%s) to full bundle (%s)" % (imgrootfs, bundle))
        swupd.path.copyxattrfiles(d, manifest_files, imgrootfs, bundle, True)
    else:
        mega_rootfs = d.getVar('MEGA_IMAGE_ROOTFS', True)
        mega_archive = d.getVar('MEGA_IMAGE_ARCHIVE', True)
        swupd.utils.create_content_manifests(mega_rootfs,
                                             fullfile + contentsuffix,
                                             fullfile + imagesuffix,
                                             unwanted_files)
        os.link(mega_archive, bundle)


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

def download_manifests(content_url, version, component, to_dir):
    """
    Download one manifest file and recursively all manifests referenced by it.
    Does not overwrite existing files. Unpacks on-the-fly using bsdtar
    and thus is independent of the compression format, as long as bsdtar
    recognizes it.
    """
    source = '%s/%d/Manifest.%s.tar' % (content_url, version, component)
    target = os.path.join(to_dir, 'Manifest.%s' % component)
    base_versions = set()
    if not os.path.exists(target):
        bb.debug(1, 'Downloading %s -> %s' % (source, target))
        response = urllib.request.urlopen(source)
        archive = response.read()
        bb.utils.mkdirhier(to_dir)
        with open(target + '.tar', 'wb') as tarfile:
            tarfile.write(archive)
        bsdtar = subprocess.Popen(['bsdtar', '-xf', '-', '-C', to_dir],
                                  stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT)
        output, _ = bsdtar.communicate(archive)
        if output or bsdtar.returncode:
            bb.fatal('Unpacking %s with bsdtar failed:\n%s' % (source, output.decode('utf-8')))
    with open(target) as f:
        # Matches the header. We might be parsing Manifest.os-core from build
        # 1000, but the actual Manifest could be from "version: 900", so get
        # that as base version, too.
        version_re = re.compile(r'^(?:previous|version):\s+(\d+)\n$')
        # Matches the individual entries.
        manifest_re = re.compile(r'^M.*\s(\d+)\s+(\S+)\n$')
        for line in f.readlines():
            m = manifest_re.match(line)
            if m:
                subversion = int(m.group(1))
                submanifest = m.group(2)
                download_manifests(content_url, subversion, submanifest, to_dir)
                base_versions.add(subversion)
            else:
                m = version_re.match(line)
                if m:
                    base_versions.add(int(m.group(1)))
    return base_versions

def download_old_versions(d):
    """
    Download the necessary information from the update repo that is needed
    to build updates in that update stream. This can run in parallel to
    a normal build and thus is not on the critical path.
    """

    content_url = d.getVar('SWUPD_CONTENT_URL', True)
    version_url = d.getVar('SWUPD_VERSION_URL', True)
    current_format = int(d.getVar('SWUPD_FORMAT', True))
    deploy_dir = d.getVar('DEPLOY_DIR_SWUPD', True)
    www_dir = os.path.join(deploy_dir, 'www')

    if not content_url or not version_url:
        bb.warn('SWUPD_CONTENT_URL and/or SWUPD_VERSION_URL not set, skipping download of old versions for the initial build of a swupd update stream.')
        return

    # Avoid double // in path. At least twisted is sensitive to that.
    content_url = content_url.rstrip('/')

    # Set up env variables with proxy information for use in urllib.
    export_proxies(d)

    # Find latest version for each of the older formats.
    # For now we ignore the released milestones and go
    # directly to the URL with all builds. The information
    # about milestones may be relevant for determining
    # how format changes need to be handled.
    latest_versions = {}
    for format in range(3, current_format + 1):
        try:
            url = '%s/version/format%d/latest' % (content_url, format)
            response = urllib.request.urlopen(url)
            version = int(response.read())
            latest_versions[format] = version
            formatdir = os.path.join(www_dir, 'version', 'format%d' % format)
            bb.utils.mkdirhier(formatdir)
            with open(os.path.join(formatdir, 'latest'), 'w') as latest:
                latest.write(str(version))
        except urllib.error.HTTPError as http_error:
            if http_error.code == 404:
                bb.debug(1, '%s does not exist, skipping that format' % url)
            else:
                raise

    # Now get the Manifests of the latest versions and the
    # versions we are supposed to provide a delta for, as a starting point.
    # In addition, we also need Manifests that provide files reused by
    # these initial set of Manifests or get referenced by them.
    #
    # There's no integrity checking for the files. bsdtar is
    # expected to detect corrupted archives and https is expected
    # to protect against man-in-the-middle attacks.
    pending_versions = set(latest_versions.values())
    pending_versions.update([int(x) for x in d.getVar('SWUPD_DELTAPACK_VERSIONS', True).split()])
    fetched_versions = set([0])
    while pending_versions:
        version = pending_versions.pop()
        sub_versions = set()
        sub_versions.update(download_manifests(content_url, version,
                                               'MoM',
                                               os.path.join(www_dir, str(version))))
        sub_versions.update(download_manifests(content_url, version,
                                               'full',
                                               os.path.join(www_dir, str(version))))
        fetched_versions.add(version)
        pending_versions.update(sub_versions.difference(fetched_versions))

    latest_version_file = os.path.join(deploy_dir, 'image', 'latest.version')
    if not os.path.exists(latest_version_file):
        # We located information about latest version from online www update repo.
        # Now use that to determine what we are updating from. Doing this here
        # instead of swupd-image.bbclass has the advantage that we can do some
        # sanity checking very early in a build.
        #
        # Building a proper update makes swupd_create_fullfiles
        # a lot faster because it allows reusing existing, unmodified files.
        # Saves a lot of space, too, because the new Manifest files then merely
        # point to the older version (no entry in ${DEPLOY_DIR_SWUPD}/www/${OS_VERSION}/files,
        # not even a link).
        if not latest_versions:
            bb.fatal("%s does not exist and no information was found under SWUPD_CONTENT_URL %s, cannot proceed without information about the previous build. When building the initial version, unset SWUPD_VERSION_URL and SWUPD_CONTENT_URL to proceed." % (latest_version_file, content_url))
        latest = sorted(latest_versions.values())[-1]
        bb.debug(2, "Setting %d in latest.version file" % latest)
        with open(latest_version_file, 'w') as f:
            f.write(str(latest))
