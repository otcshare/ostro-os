DESCRIPTION = "SSH implementation in Java"
HOMEPAGE = "http://www.jcraft.com/jsch"
LICENSE = "BSD"
LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=55e3b6a0987ccd0c34530f3df2d206ae"

SRC_URI = "${SOURCEFORGE_MIRROR}/jsch/jsch-${PV}.zip"

inherit java-library

DEPENDS = "jzlib"
DEPENDS_virtclass-native = "jzlib-native"

RDEPENDS_${PN} = "libjzlib-java"
RDEPENDS_${PN}_virtclass-native = ""

do_compile() {
  mkdir -p build

  oe_makeclasspath cp -s jzlib

  javac -sourcepath src -cp $cp -d build `find src -name "*.java"`

  fastjar -C build -c -f ${JARFILENAME} .
}

SRC_URI[md5sum] = "b59cec19a487e95aed68378976b4b566"
SRC_URI[sha256sum] = "ca9d2ae08fd7a8983fb00d04f0f0c216a985218a5eb364ff9bee73870f28e097"

NATIVE_INSTALL_WORKS = "1"
BBCLASSEXTEND = "native"

