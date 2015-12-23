DESCRIPTION = "Java Regular Expression package"
AUTHOR = "Apache Software Foundation"
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=86d3f3a95c324c9479bd8986968f4327"
PR = "r1"

SRC_URI = "http://archive.apache.org/dist/jakarta/regexp/source/jakarta-${BP}.tar.gz"

inherit java-library

S = "${WORKDIR}/jakarta-${BP}"

do_compile() {
  mkdir -p build

  javac -sourcepath src/java -d build `find src/java -name \*.java`

  fastjar cf ${JARFILENAME} -C build .
}

SRC_URI[md5sum] = "b941b8f4de297827f3211c2cb34af199"
SRC_URI[sha256sum] = "79e80af8cbeb68ddad75a1aa6244d7acd62176bfd69bcdc0640d11177dcde97d"

BBCLASSEXTEND = "native"

