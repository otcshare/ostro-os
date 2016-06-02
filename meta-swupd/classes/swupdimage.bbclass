# Used by swupd-image.bbclass to generate additional images as
# configured by SWUPD_IMAGES.
#
# These additional images are virtual image recipes with
# empty do_rootfs and a do_image which merely copies the
# relevant content from the mega bundle.
#
# They do not get built by default. One has to request building
# them explictly. For example:
#
# SWUPD_BUNDLES = "foo"
# BUNDLE_CONTENTS[foo] = "foo-bar"
# SWUPD_IMAGES = "extended"
# SWUPD_IMAGES[extended] = "foo"
#
# $ bitbake core-image-minimal
# $ bitbake core-image-minimal-extended

python swupdimage_virtclass_handler () {
    pn = e.data.getVar("PN", True)
    cls = e.data.getVar("BBEXTENDCURR", True)
    imageext = e.data.getVar("BBEXTENDVARIANT", True)

    if cls != 'swupdimage':
        return

    if not imageext:
        bb.fatal('swupdimage must be used with a parameter i.e. BBCLASSEXTEND="swupdimage:foo"')

    # Rename the virtual recipe to create the desired image variant.
    e.data.setVar("PN_BASE", pn)
    pn_base = pn
    pn = pn + '-' + imageext
    e.data.setVar("PN", pn)

    # Sanity check settings to catch errors already during parsing.
    imagebundles = (e.data.getVarFlag('SWUPD_IMAGES', imageext, True) or '').split()
    if not imagebundles:
        bb.fatal('SWUPD_IMAGES[%s] is not set, this should list the bundles which are to be added to the base image.' % imageext)
    bundles = (e.data.getVar('SWUPD_BUNDLES', True) or "").split()
    for bundle in imagebundles:
        if not bundle in bundles:
            bb.fatal('%s from SWUPD_IMAGES[%s] is not the name of a bundle.' % (bundle, imageext))
    if len(set(imagebundles)) != len(imagebundles):
        bb.fatal('SWUPD_IMAGES[%s] contains duplicate entries' % imageext)

    # Needed by do_image_append() in swupd-image.bbclass.
    e.data.setVar("IMAGE_BUNDLE_NAME", imageext)
    # We override the default methods such that they only copy from the mega rootfs.
    e.data.setVar("do_image", "    import swupd.rootfs\n    swupd.rootfs.create_rootfs(d)\n")
    e.data.setVar("do_rootfs", "")
    # Depend on complete bundle generation in the base image.
    dep = ' %s:do_stage_swupd_inputs' % pn_base
    e.data.appendVarFlag('do_image', 'depends', dep)
}

addhandler swupdimage_virtclass_handler
swupdimage_virtclass_handler[eventmask] = "bb.event.RecipePreFinalise"
