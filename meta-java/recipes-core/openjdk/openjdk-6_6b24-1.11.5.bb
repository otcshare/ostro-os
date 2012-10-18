require openjdk-6-release-6b24.inc

PR = "${INC_PR}.0"

SRC_URI[iced.md5sum] = "db3338c4fa8977eef5bd3f059f716407"
SRC_URI[iced.sha256sum] = "258d81d957f8ab9322fbaf7c90647f27f6b4e675504fa279858e6dfe513f7574"

ICEDTEAPATCHES += "file://icedtea-jdk-rmi-crosscompile.patch;apply=no"

DISTRIBUTION_PATCHES += "patches/icedtea-jdk-rmi-crosscompile.patch"
