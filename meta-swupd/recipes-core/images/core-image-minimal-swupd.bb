require recipes-core/images/core-image-minimal.bb

DESCRIPTION = "A small image just capable of allowing a device to boot, \
update and add new features with swupd"

inherit swupd-image

