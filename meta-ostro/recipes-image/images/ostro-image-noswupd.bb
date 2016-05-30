SUMMARY = "Ostro image for local builds with swupd disabled."
DESCRIPTION = "Ostro image for local builds with swupd disabled. The default content matches the one from ostro-image-swupd. This is the recommended image when testing whether Ostro OS works on a device, because it builds faster than ostro-image-swupd and contains some useful systemd debugging tools for interactive use and, last but not least, an SSH server."

# In normal images without swupd it is possible to set per-image
# variables for a specific image recipe using the the _pn-<image name>
# notation.  However, that stops working once the swupd feature gets
# enabled (because that internally relies on virtual images under
# different names), so the recommended approach is to have per-recipe
# variables (like OSTRO_IMAGE_NOSWUPD_EXTRA_FEATURES) and customize
# those outside the recipe:
OSTRO_IMAGE_NOSWUPD_EXTRA_FEATURES ?= "${OSTRO_IMAGE_FEATURES_REFERENCE}"
OSTRO_IMAGE_NOSWUPD_EXTRA_INSTALL ?= "${OSTRO_IMAGE_INSTALL_REFERENCE}"
OSTRO_IMAGE_EXTRA_FEATURES += "${OSTRO_IMAGE_NOSWUPD_EXTRA_FEATURES}"
OSTRO_IMAGE_EXTRA_INSTALL += "${OSTRO_IMAGE_NOSWUPD_EXTRA_INSTALL}"

# If the default "ostro-image-noswupd" name is
# undesirable, write a custom image recipe similar to this one here (although
# ostro-image-minimal.bb might be a better starting point), or customize the
# image file names when continuing to use ostro-image-noswupd.bb.
#
# Example for customization in local.conf when building ostro-image-noswupd.bb:
# IMAGE_BASENAME_pn-ostro-image-noswupd = "my-ostro-image-reference"
# OSTRO_IMAGE_NOSWUPD_EXTRA_INSTALL_append = "my-own-package"
# OSTRO_IMAGE_NOSWUPD_EXTRA_FEATURES_append = "dev-pkgs"

inherit ostro-image
