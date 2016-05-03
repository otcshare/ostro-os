DESCRIPTION = "Tcl interpreter for Java"
LICENSE = "UCB & SUN & AMD & CDS"
LIC_FILES_CHKSUM = " \
                    file://license.ucb;md5=997c6617d2f2a747e39945c0f2d1a264 \
                    file://license.terms;md5=ce3ac33515250b3a438b2633ccb29aac \
                    file://license.itcl;md5=52f12c6c2c239f3481edb3e52fc638b8 \
                    file://license.amd;md5=a286e569daafb1cf4c3f943d354badab \
                   "

HOMEPAGE = "http://sourceforge.net/projects/tcljava"

SRC_URI = "http://downloads.sourceforge.net/tcljava/jacl${PV}.tar.gz"

inherit java-library

S = "${WORKDIR}/jacl${PV}"

do_compile() {
  mkdir -p build

  javac -sourcepath src/tcljava:src/jacl -d build `find src/tcljava src/jacl -name "*.java"`

  fastjar cf ${JARFILENAME} -C build .
}

SRC_URI[md5sum] = "a7ec8300e8933164e854460c73ac6269"
SRC_URI[sha256sum] = "0edac0a7d2253c29c44ccc92427fa9ad4ee81b6c82142e417f72399a8584b749"

BBCLASSEXTEND = "native"
