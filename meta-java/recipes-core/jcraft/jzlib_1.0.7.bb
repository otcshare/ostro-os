DESCRIPTION = "zlib implementation in Java"
LICENSE = "BSD"
LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=a2b2e5b95bf768dd5c4ca097c9cde9e9"

HOMEPAGE = "http://www.jcraft.com/jzlib"

SRC_URI = "http://www.jcraft.com/jzlib/jzlib-${PV}.tar.gz"

inherit java-library

do_compile() {
  mkdir -p build

  javac -sourcepath . -d build `find com -name "*.java"`

  fastjar -C build -c -f ${JARFILENAME} .
}

SRC_URI[md5sum] = "3c52a0afb970e8a1fb2d34f30d330a83"
SRC_URI[sha256sum] = "20923a3f771a14c58c8cddfff2b589d568aff09f8a931919dc63ddaabb32407a"

NATIVE_INSTALL_WORKS = "1"
BBCLASSEXTEND = "native"

