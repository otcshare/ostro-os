DESCRIPTION = "Lexical analyzer generator for Java"
AUTHOR = "Elliot Berk, A. Appel, C. Scott Ananian"
LICENSE = "CUP"
LIC_FILES_CHKSUM = "file://${WORKDIR}/LICENSE;md5=2c9db91c00f38e52cfc8e67bafaa7c33"


RDEPENDS_${PN} = "java2-runtime"
RDEPENDS_${PN}_virtclass-native = ""

inherit java-library

SRC_URI = "http://www.cs.princeton.edu/~appel/modern/java/CUP/java_${BPN}_v10k.tar.gz \
	   file://cup \
	  "

S = "${WORKDIR}/java_cup"

do_configure() {
	sed -i \
		-e "s|OE_STAGING_BINDIR|${bindir}|" \
		-e "s|OE_STAGING_DATADIR_JAVA|${data_java}|" \
		-e "s|OE_CUP_JAR|${BP}.jar|" \
		${WORKDIR}/cup
}

do_compile() {
	mkdir -p build

	javac -d build `find . -name "*.java"`

	fastjar cf ${BP}.jar -C build .
}

do_install_append() {
	install -d ${D}${bindir}
	install -m 0755 ${WORKDIR}/cup ${D}${bindir}
}

PACKAGES = "${PN}"

FILES_${PN} += "${datadir_java}"

SRC_URI[md5sum] = "8b11edfec13c590ea443d0f0ae0da479"
SRC_URI[sha256sum] = "7e6dc5be74ae56c7e86e69ad0ad88dae3b2847afa9e73a76635918a6b1eb75cd"

BBCLASSEXTEND = "native"

