SUMMARY = "Ostro image with swupd enabled."

# Image configuration changes cannot be done using the
# _pn-ostro-image-swupd notation, because then the configuration of
# this base image and the virtual images created from it would be
# different.
#
# Instead extend these variables.
OSTRO_IMAGE_SWUPD_EXTRA_FEATURES ?= ""
OSTRO_IMAGE_SWUPD_EXTRA_INSTALL ?= ""
OSTRO_IMAGE_EXTRA_FEATURES += "${OSTRO_IMAGE_SWUPD_EXTRA_FEATURES}"
OSTRO_IMAGE_EXTRA_INSTALL += "${OSTRO_IMAGE_SWUPD_EXTRA_INSTALL}"

# Enable swupd.
OSTRO_IMAGE_EXTRA_FEATURES += "swupd"

# ostro-image-swupd as build target only triggers
# the creation of swupd bundles without creating "ostro-image-swupd"
# image files, because those would not be very useful (too minimal).
# Instead, images can get created for the default SWUPD_IMAGES.
OSTRO_VM_IMAGE_TYPES_pn-ostro-image-swupd = ""
IMAGE_FSTYPES_pn-ostro-image-swupd = ""

# Inherit the base class after changing relevant settings like
# the image features, because the class looks at them at the time
# when it gets inherited.
inherit ostro-image
