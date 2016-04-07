# Use the pre-generated keys for IMA signing.
IMA_EVM_KEY_DIR = "${IMA_EVM_BASE}/data/debug-keys"

# Enable local root access. Always use _append, to
# avoid getting this change overwritten by a
# OSTRO_IMAGE_EXTRA_FEATURES = "foo" in local.conf.
OSTRO_IMAGE_EXTRA_FEATURES_append = " autologin"

# Mark images as "development" by extending /etc/motd.
OSTRO_EXTRA_MOTD () {
************************************
*** This is a development image! ***
*** Do not use in production.    ***
************************************
}

# Extend the default package selection and image configuration of the
# no-swupd "ostro-image" to match the content of the swupd
# "ostro-image-swupd-reference".
OSTRO_IMAGE_NOSWUPD_EXTRA_FEATURES_append = " ${OSTRO_DEVELOPMENT_EXTRA_FEATURES}"
OSTRO_IMAGE_NOSWUPD_EXTRA_INSTALL_append = " ${OSTRO_DEVELOPMENT_EXTRA_INSTALL}"
OSTRO_DEVELOPMENT_EXTRA_FEATURES ?= "${OSTRO_IMAGE_FEATURES_REFERENCE}"
OSTRO_DEVELOPMENT_EXTRA_INSTALL ?= "${OSTRO_IMAGE_INSTALL_REFERENCE}"

# Everything ready, avoid initial sanity check.
OSTRO_IMAGE_BUILD_MODE_SELECTED = "1"

