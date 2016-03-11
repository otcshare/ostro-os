
SYSLINUX_LABELS_VM ?= "boot"
LABELS_VM ?= "${SYSLINUX_LABELS_VM}"

# Using an initramfs is optional. Enable it by setting INITRD_IMAGE_VM.
INITRD_IMAGE_VM ?= ""
INITRD_VM ?= "${@'${DEPLOY_DIR_IMAGE}/${INITRD_IMAGE_VM}-${MACHINE}.cpio.gz' if '${INITRD_IMAGE_VM}' else ''}"
do_bootdirectdisk[depends] += "${@'${INITRD_IMAGE_VM}:do_image_complete' if '${INITRD_IMAGE_VM}' else ''}"

# need to define the dependency and the ROOTFS for directdisk
do_bootdirectdisk[depends] += "${PN}:do_image_ext4"
ROOTFS ?= "${DEPLOY_DIR_IMAGE}/${IMAGE_NAME}${IMAGE_NAME_SUFFIX}.ext4"

# creating VM images relies on having a hdddirect so ensure we inherit it here.
inherit boot-directdisk

IMAGE_TYPEDEP_hdddirect = "ext4"
IMAGE_TYPES_MASKED += "hdddirect"
