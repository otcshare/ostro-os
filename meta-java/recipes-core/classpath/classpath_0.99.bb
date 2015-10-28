require classpath.inc

inherit distro_features_check

REQUIRED_DISTRO_FEATURES = "x11"

LIC_FILES_CHKSUM = "file://LICENSE;md5=92acc79f1f429143f4624d07b253702a"

SRC_URI += " \
            file://sun-security-getproperty.patch;striplevel=0 \
            file://ecj_java_dir.patch \
            file://autotools.patch \
            file://miscompilation.patch \
            file://toolwrapper-exithook.patch \
            file://use_libdir.patch \
            file://freetype2.patch \
           "

SRC_URI[md5sum] = "0ae1571249172acd82488724a3b8acb4"
SRC_URI[sha256sum] = "f929297f8ae9b613a1a167e231566861893260651d913ad9b6c11933895fecc8"
