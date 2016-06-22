FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

LINUX_VERSION = "3.10.98"
#LINUX_VERSION = "3.19.5"

SRC_URI = "git://github.com/01org/edison-linux.git;protocol=git;branch=edison-${LINUX_VERSION};nocheckout=1;name=machine"
SRC_URI += "file://defconfig"
SRC_URI += "file://4.2-3.10-hack.patch"
SRC_URI += "file://0002-Always-inline-inline-functions.patch"

SRCREV_machine = "ff2ff63071c8cf7408c2bed7350c155586c869dc"
#SRCREV_machine = "e152349de59b43b2a75f2c332b44171df461d5a0"

inherit kernel
require recipes-kernel/linux/linux-yocto.inc

PV = "${LINUX_VERSION}+git${SRCPV}"

COMPATIBLE_MACHINE = "edison"

