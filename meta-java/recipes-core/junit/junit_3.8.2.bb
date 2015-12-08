DESCRIPTION = "JUnit is a testing framework for Java"
AUTHOR = "junit.org"
HOMEPAGE = "http://www.junit.org"
LICENSE = "CPL-1.0"
LIC_FILES_CHKSUM = "file://cpl-v10.html;md5=67a4b75d42edcbd82d2878eba913691b"
PR = "r1"

SRC_URI = "http://downloads.sourceforge.net/junit/junit${PV}.zip"

S = "${WORKDIR}/junit${PV}"

DEPENDS += "unzip-native"

inherit java-library java-bootstrap-components

do_unpackpost() {
	mkdir -p src
	# Prevent deletion by do_removebinaries.
	if [ -e src.jar ]; then
		mv src.jar src.zip
	fi
	unzip -o src.zip -d src
}

addtask unpackpost before do_removebinaries after do_unpack

do_compile() {
  mkdir -p build

	# Workaround for jamvm.
	#bcp=${STAGING_DATADIR_NATIVE}/classpath/glibj.zip

  javac -sourcepath src -d build `find src -name "*.java"`

  fastjar cf ${JARFILENAME} -C build .
}

SRC_URI[md5sum] = "9b8963ba2147a64bd5f1574b6fd289cb"
SRC_URI[sha256sum] = "aae23d20e6f4dc45b4bf0b10fedcbd209c100342a0cafce1aa07d2da6da1f24a"

BBCLASSEXTEND = "native"
