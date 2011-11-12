DESCRIPTION = "Java Bytecode manipulation library"
AUTHOR = "Apache Software Foundation"
LICENSE = "AL2.0"
LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=44030f19e8bad73725f39d16fd05ff12"

SRC_URI = "http://archive.apache.org/dist/jakarta/bcel/source/${BP}-src.tar.gz"

inherit java-library

DEPENDS = "xerces-j regexp"
DEPENDS_virtclass-native = "xerces-j-native regexp-native"


do_compile() {
  mkdir -p build

  oe_makeclasspath cp -s xercesImpl regexp

  javac -sourcepath src/java -d build -cp $cp `find src/java -name \*.java`

  fastjar -C build -c -f ${JARFILENAME} .
}

SRC_URI[md5sum] = "905b7e718e30e7ca726530ecf106e532"
SRC_URI[sha256sum] = "68039d59a38379d7b65ea3fc72276c43ba234776460e14361af35771bcaab295"

NATIVE_INSTALL_WORKS = "1"
BBCLASSEXTEND = "native"

