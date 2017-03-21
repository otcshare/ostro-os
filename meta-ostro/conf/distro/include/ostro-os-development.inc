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

# Everything ready, avoid initial sanity check.
OSTRO_IMAGE_BUILD_MODE_SELECTED = "1"

# Test build
OSTRO_IMAGE_EXTRA_INSTALL_append = " librealsense-examples"
