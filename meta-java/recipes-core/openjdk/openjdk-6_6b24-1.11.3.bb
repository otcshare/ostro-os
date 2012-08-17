require openjdk-6-release-6b24.inc

PR = "${INC_PR}.0"

SRC_URI[iced.md5sum] = "52e0db92541296bdf43a4cfce135ac4f"
SRC_URI[iced.sha256sum] = "7d91c407b9795bd6f6255bcf0fb808416b36418c57f601dc47cfabff83194cf4"

ICEDTEAPATCHES += "file://icedtea-jdk-rmi-crosscompile.patch;apply=no"

DISTRIBUTION_PATCHES += "patches/icedtea-jdk-rmi-crosscompile.patch"
