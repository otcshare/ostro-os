DESCRIPTION = "Design quality metrics generator for each Java"

# see http://www.clarkware.com/software/license.txt
LICENSE = "BSD"
LIC_FILES_CHKSUM = "file://LICENSE;md5=f5777d32a7709d558c2877d4a6616230"

HOMEPAGE = "http://clarkware.com/software/JDepend.html"

SRC_URI = "http://www.clarkware.com/software/jdepend-${PV}.zip"

inherit java-library

do_compile() {
  mkdir -p build

  javac -sourcepath src -d build `find src -name "*.java"`

  fastjar -C build -c -f ${JARFILENAME} .
}

SRC_URI[md5sum] = "0cbaf43493cd30838bee261f69e76fe9"
SRC_URI[sha256sum] = "b9f34236aaea5ddc070caa29794d2f5ae79bc12e199bec6ebba6c29093a17a9e"

BBCLASSEXTEND = "native"
