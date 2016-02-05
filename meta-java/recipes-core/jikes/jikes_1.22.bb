DESCRIPTION = "Java compiler adhering to language and VM specifications"
HOMEPAGE = "http://jikes.sourceforge.net/"
PRIORITY = "optional"
SECTION = "devel"
LICENSE = "IPL-1.0"
LIC_FILES_CHKSUM = " \
                    file://COPYING;md5=2d52359fd0d8f0c3e371e4cd19b213c0 \
                    file://doc/license.htm;md5=43506e48033a385dc0936f620ae2c745 \
                   "
SRC_URI = "${SOURCEFORGE_MIRROR}/jikes/jikes-${PV}.tar.bz2"

inherit autotools update-alternatives

BBCLASSEXTEND = "native"

RDEPENDS_${PN} = "classpath"
PROVIDES_virtclass-native = ""
RDEPENDS_${PN}_virtclass-native = ""

EXTRA_OECONF = "--disable-fp-emulation --enable-source15"

# configure script incorrectly defines these when cross compiling for ARM
CXXFLAGS_append_arm += "-UHAVE_64BIT_TYPES -DWORDS_BIGENDIAN=1"

do_install() {
    oe_runmake 'DESTDIR=${D}' install
    ln -s ${bindir}/jikes ${D}${bindir}/javac.jikes
}

PROVIDES = "virtual/javac"
ALTERNATIVE_${PN} = "javac"
ALTERNATIVE_LINK = "/usr/bin/javac"
ALTERNATIVE_TARGET = "${bindir}/javac.jikes"

SRC_URI[md5sum] = "cda958c7fef6b43b803e1d1ef9afcb85"
SRC_URI[sha256sum] = "0cb02c763bc441349f6d38cacd52adf762302cce3a08e269f1f75f726e6e14e3"
