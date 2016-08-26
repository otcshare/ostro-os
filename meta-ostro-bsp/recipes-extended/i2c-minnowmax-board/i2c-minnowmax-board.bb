DESCRIPTION = "I2C sensor kernel modules on Minnow-Max"

LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://${THISDIR}/files/COPYING;md5=12f884d2ae1ff87c09e5b7ccc2c4ca7e"
PR = "r0"

inherit module

FILESEXTRAPATHS_prepend := "${THISDIR}/files/:"

SRC_URI = "file://i2c-minnow-mpu6050.c \
           file://i2c-minnow-apds9960.c \
           file://Makefile \
           "

S = "${WORKDIR}"
