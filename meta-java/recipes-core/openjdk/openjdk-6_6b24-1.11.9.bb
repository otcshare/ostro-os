require openjdk-6-release-6b24.inc

PR = "${INC_PR}.0"

SRC_URI[iced.md5sum] = "1826c4bfb4faae1e820dd8997428a831"
SRC_URI[iced.sha256sum] = "0c134bea8d48c77ad5d41d4a0f98f471c381faaa0ef0c215d48687e709e93f3f"

ICEDTEAPATCHES += "file://icedtea-jdk-rmi-crosscompile.patch;apply=no"

DISTRIBUTION_PATCHES += "patches/icedtea-jdk-rmi-crosscompile.patch"
