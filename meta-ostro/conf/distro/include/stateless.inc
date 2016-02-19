INHERIT += "stateless"

###########################################################################

# Temporary overrides until Ostro OS is fully stateless.

# This entry here allows everything in /etc because Ostro OS is
# not actually stateless yet. We merely use the stateless.bbclass
# to remove files from /etc which get written on the device
# and thus must be excluded from images and, more importantly,
# swupd bundles.
STATELESS_ETC_WHITELIST += "*"

# Empty directories must be kept.
STATELESS_ETC_DIR_WHITELIST += "*"

###########################################################################
