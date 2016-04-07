SUMMARY = "Ostro image for local builds with swupd disabled."

# Image configuration cannot always be done using the _pn-ostro-image
# notation, because then the configuration of the base image and
# potential virtual images created from it would be different.
#
# Instead extend these variables. We cannot just use OSTRO_IMAGE_EXTRA_FEATURES
# and OSTRO_IMAGE_EXTRA_INSTALL because those affect all images based
# on ostro-image.bbclass.
OSTRO_IMAGE_NOSWUPD_EXTRA_FEATURES ?= ""
OSTRO_IMAGE_NOSWUPD_EXTRA_INSTALL ?= ""
OSTRO_IMAGE_EXTRA_FEATURES += "${OSTRO_IMAGE_NOSWUPD_EXTRA_FEATURES}"
OSTRO_IMAGE_EXTRA_INSTALL += "${OSTRO_IMAGE_NOSWUPD_EXTRA_INSTALL}"

inherit ostro-image
