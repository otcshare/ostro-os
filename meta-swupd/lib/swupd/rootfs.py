import os
import bb
import oe.path
from swupd.utils import manifest_to_file_list
from swupd.path import copyxattrfiles


def create_rootfs(d):
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
            rootfs_contents.append(entry[2:])
        # clean up
        os.unlink(outfile)
    else: # non-base image, i.e. swupdimage
        manifest = d.expand("${DEPLOY_DIR_SWUPD}/image/${OS_VERSION}/${PN_BASE}${SWUPD_ROOTFS_MANIFEST_SUFFIX}")
        for entry in manifest_to_file_list(manifest):
            rootfs_contents.append(entry[2:])

    bb.debug(3, 'rootfs_contents has %s entries' % (len(rootfs_contents)))
    for bundle in imagebundles:
        manifest = d.expand("${DEPLOY_DIR_SWUPD}/image/${OS_VERSION}/bundle-${PN_BASE}-%s${SWUPD_ROOTFS_MANIFEST_SUFFIX}") % bundle
        for entry in manifest_to_file_list(manifest):
            rootfs_contents.append(entry[2:])

    bb.debug(2, 'Re-copying rootfs contents from mega image')
    copyxattrfiles(d, rootfs_contents, d.getVar('MEGA_IMAGE_ROOTFS', True), rootfs)

    # Create .rootfs.manifest for bundle images as the union of all
    # contained bundles. Otherwise the image wouldn't have that file,
    # which breaks certain image types ("toflash" in the Edison BSP)
    # and utility classes (like isafw.bbclass).
    if imageext:
        packages = set()
        manifest = d.getVar('IMAGE_MANIFEST', True)
        for bundle in imagebundles:
            bundlemanifest = manifest.replace(pn, 'bundle-%s-%s' % (pn_base, bundle))
            if not os.path.exists(bundlemanifest):
                dt = d.expand('-${DATETIME}.rootfs')
                bundlemanifest = bundlemanifest.replace(dt, '')
            with open(bundlemanifest) as f:
                 packages.update(f.readlines())
        with open(manifest, 'w') as f:
            f.writelines(sorted(packages))
