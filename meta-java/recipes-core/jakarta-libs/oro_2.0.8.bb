DESCRIPTION = "Perl5-compatible regular expressions library for Java"
AUTHOR = "Apache Software Foundation"
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=372b1e91335021ca74173b2ab4dc97dd"
PR = "r1"

SRC_URI = "http://archive.apache.org/dist/jakarta/oro/source/jakarta-${BP}.tar.gz"

inherit java-library

S = "${WORKDIR}/jakarta-${BP}"

do_compile() {
  mkdir -p build

  javac -sourcepath src/java -d build `find src/java -name \*.java`

  fastjar -C build -c -f ${JARFILENAME} org
}

SRC_URI[md5sum] = "6f7690c6ba9750e3cbb8ebd10078a79a"
SRC_URI[sha256sum] = "4c4f3c7c479994c3ce09f542d4fbdc03eed58a2d7f320d32f2baf238b5b6f566"

BBCLASSEXTEND = "native"
