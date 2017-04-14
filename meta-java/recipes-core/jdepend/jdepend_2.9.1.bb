DESCRIPTION = "Design quality metrics generator for each Java"

# see https://github.com/clarkware/jdepend/blob/master/LICENSE
LICENSE = "BSD"
LIC_FILES_CHKSUM = "file://LICENSE;md5=f5777d32a7709d558c2877d4a6616230"

HOMEPAGE = "https://github.com/clarkware/jdepend"

SRC_URI = "https://github.com/clarkware/jdepend/archive/${PV}.zip"

inherit java-library

do_compile() {
  mkdir -p build

  javac -sourcepath src -d build `find src -name "*.java"`

  fastjar cf ${JARFILENAME} -C build .
}

SRC_URI[md5sum] = "9b91efe1d770e023893f89f4dde8434e"
SRC_URI[sha256sum] = "536b5082d64e4f4dddd514ce30178f36c7a31b34d969275f278f72e522e7f7c9"

BBCLASSEXTEND = "native"
