require openjdk-6-release-6b24.inc

PR = "${INC_PR}.0"

SRC_URI[iced.md5sum] = "3dd02bc93e7f1cd7d59c0aef20f6c9f7"
SRC_URI[iced.sha256sum] = "62620b5544d5e1df7508d7c777fb78532c75eec43b99c8c7d1a3c84f352c1ea3"

ICEDTEAPATCHES += "file://icedtea-jdk-rmi-crosscompile.patch;apply=no"

DISTRIBUTION_PATCHES += "patches/icedtea-jdk-rmi-crosscompile.patch"
