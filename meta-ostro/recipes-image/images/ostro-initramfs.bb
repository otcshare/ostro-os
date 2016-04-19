# Ostro OS initramfs image. Derived from core-image-minimal-initramfs,
# with initramfs-framework instead of initramfs-live-boot and
# initramfs-live-install.
#
# Debugging tips for local.conf:
# SYSLINUX_PROMPT = "100" - show menu for 10 seconds
# AUTO_SYSLINUXMENU = "1" - automatically generate menu with choice between graphics and serial boot
# SYSLINUX_TIMEOUT = "100" - boot after waiting for 10 seconds

DESCRIPTION = "Small image capable of booting a device. The kernel includes \
the Minimal RAM-based Initial Root Filesystem (initramfs), which finds the \
first 'init' program more efficiently."

PACKAGE_INSTALL = "${VIRTUAL-RUNTIME_base-utils} base-passwd ${ROOTFS_BOOTSTRAP_INSTALL} ${FEATURE_INSTALL}"

# e2fs: loads fs modules and adds ext2/ext3/ext4=<device>:<path> boot parameter
#       for mounting additional partitions

# used to detect boot devices automatically
PACKAGE_INSTALL += "initramfs-module-udev"

# debug: adds debug boot parameters like 'shell' and 'debug', see
#        meta/recipes-core/initrdscripts/initramfs-framework/debug for details
# Could be removed in more minimal product image.
PACKAGE_INSTALL += "initramfs-module-debug"

# Do not pollute the initrd image with rootfs features
IMAGE_FEATURES = ""

# Instead we have additional image feature(s).
IMAGE_FEATURES[validitems] += " \
    ima \
"
IMAGE_FEATURES += " \
    ${@bb.utils.contains('DISTRO_FEATURES', 'ima', 'ima', '', d)} \
"
FEATURE_PACKAGES_ima = "initramfs-framework-ima"

IMAGE_LINGUAS = ""

LICENSE = "MIT"

IMAGE_FSTYPES = "${INITRAMFS_FSTYPES}"
inherit core-image

BAD_RECOMMENDATIONS += "busybox-syslog"

# Ensure that we install the additional files needed for IMA/EVM
# by inheriting ima-evm-rootfs, even though no files need to be
# signed in the initramfs itself.
#
# For the rootfs we use the IMA example policy which allows both
# signed and hashed files (installed as part of
# initramfs-framework-ima.bb) and sign the rootfs accordingly (in
# ostro-image.bb).
IMA_EVM_ROOTFS_SIGNED = "-maxdepth 0 -false"
IMA_EVM_ROOTFS_HASHED = "-maxdepth 0 -false"
IMA_EVM_ROOTFS_CLASS = "${@bb.utils.contains('IMAGE_FEATURES', 'ima', 'ima-evm-rootfs', '',d)}"
inherit ${IMA_EVM_ROOTFS_CLASS}
