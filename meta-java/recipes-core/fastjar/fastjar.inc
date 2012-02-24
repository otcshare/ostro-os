DESCRIPTION = "jar replacement written in C."
HOMEPAGE = "http://savannah.nongnu.org/projects/fastjar/"
SECTION = "devel"
PRIORITY = "optional"
LICENSE = "GPLv2"
PR = "r1"

DEPENDS = "zlib"

SRC_URI = "http://download.savannah.nongnu.org/releases/fastjar/fastjar-${PV}.tar.gz"

inherit autotools update-alternatives

PACKAGES = "${PN}-grepjar ${PN} ${PN}-dbg ${PN}-doc"
FILES_${PN}-grepjar = "${bindir}/grepjar"

PROVIDES = "virtual/jar"
ALTERNATIVE_NAME = "jar"
ALTERNATIVE_LINK = "${bindir}/jar"
ALTERNATIVE_PATH = "${bindir}/fastjar"

BBCLASSEXTEND = "native"
