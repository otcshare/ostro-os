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

SRC_URI[md5sum] = "4e979c0dda766ba1dd719905ca975c7b"
SRC_URI[sha256sum] = "202de62e2f3d0667cc464720d5897d0ccb29767ec24e0a4d4c5bd6c4d37425a4"

NATIVE_INSTALL_WORKS = "1"
BBCLASSEXTEND = "native"
