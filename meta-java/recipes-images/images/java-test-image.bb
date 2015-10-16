LICENSE = "MIT"

inherit core-image

IMAGE_LINGUAS = " "


IMAGE_INSTALL = "busybox modutils-initscripts initscripts opkg udev sysvinit netbase base-files base-passwd \
                 ${ROOTFS_PKGMANAGE_BOOTSTRAP} ${CORE_IMAGE_EXTRA_INSTALL} \
                 openjdk-7-jre openjdk-7-vm-zero \
                 strace dropbear binutils \
                 classpath \
                 classpath-common \
                 classpath-examples \
                 classpath-tools \
"
