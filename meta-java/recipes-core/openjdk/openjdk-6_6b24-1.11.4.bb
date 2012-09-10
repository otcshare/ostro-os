require openjdk-6-release-6b24.inc

PR = "${INC_PR}.0"

SRC_URI[iced.md5sum] = "a5a3a5aeaba0ddf4c9fdf8e899bf77c2"
SRC_URI[iced.sha256sum] = "7bc0037514aedbbd5e65edcb2fa300a18285688d27b359c2144fcf563174e4fd"

ICEDTEAPATCHES += "file://icedtea-jdk-rmi-crosscompile.patch;apply=no"

DISTRIBUTION_PATCHES += "patches/icedtea-jdk-rmi-crosscompile.patch"
