#
# BSP variables and settings specific to the meta-intel layer.
# You must include the meta-intel layer in your bblayers.conf
# to use them.
#

#
# XSERVER subcomponents, used to build the XSERVER variable
#

PREFERRED_PROVIDER_virtual/kernel ?= "linux-yocto"
PREFERRED_VERSION_linux-yocto ?= "4.4%"

# for Xserver older than 1.13.0
OLD_XSERVER_X86_EXT = "xserver-xorg-extension-dri \
           xserver-xorg-extension-dri2 \
           xserver-xorg-extension-extmod \
           xserver-xorg-extension-dbe \
           "

XSERVER_X86_MATROX_MGA = "xf86-video-mga \
           "

XSERVER_X86_ASPEED_AST = "xf86-video-ast \
           "

# include the user space intel microcode loading support in the generated images.
MACHINE_ESSENTIAL_EXTRA_RDEPENDS_append = "${@bb.utils.contains('MACHINE_FEATURES', 'intel-ucode', ' intel-microcode', '', d)}"

# for the early boot time kernel microcode loading support,
# merge the microcode data in the final initrd image.
INITRD_LIVE_prepend = "${@bb.utils.contains('MACHINE_FEATURES', 'intel-ucode', '${DEPLOY_DIR_IMAGE}/microcode.cpio ', '', d)}"
