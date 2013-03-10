require openjdk-6-release-6b27.inc

PR = "${INC_PR}.0"

SRC_URI[iced.md5sum] = "85bfc656c20fb762b72b71d3492a326c"
SRC_URI[iced.sha256sum] = "eb326c6ae0147ca4abe4bd79e52c1edc2ef08e5e008230e24bee3abb39e14dda"

ICEDTEAPATCHES += "file://icedtea-jdk-rmi-crosscompile.patch;apply=no"

DISTRIBUTION_PATCHES += "patches/icedtea-jdk-rmi-crosscompile.patch"
