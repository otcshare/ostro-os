DESCRIPTION = "Lexical analyzer generator for Java"
LICENSE = "MPL-2.0"
LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=8e2372bdbf22c99279ae4599a13cc458"

BBCLASSEXTEND = "native"

inherit java-library

SRC_URI = "\
	https://github.com/downloads/mozilla/rhino/rhino1_7R4.zip \
	file://rhino \
	file://rhino-jsc \
	"

S = "${WORKDIR}/rhino1_7R4"

PACKAGES = "${JPN} rhino"

FILES_${PN} = "${bindir}/rhino ${bindir}/rhino-jsc"
RDEPENDS_${PN} = "java2-runtime ${JPN}"
RDEPENDS_${PN}_virtclass-native = ""

do_compile() {
	mkdir -p build

	# Compatibility fix for jamvm which has non-genericised
	# java.lang classes. :(
	bcp_arg="-bootclasspath ${STAGING_DATADIR_NATIVE}/classpath/glibj.zip"

	javac $bcp_arg -source 1.6 -sourcepath src -d build `find src -name "*.java"`

	mkdir -p build/org/mozilla/javascript/resources
	cp src/org/mozilla/javascript/resources/*.properties build/org/mozilla/javascript/resources

	fastjar cfm ${JARFILENAME} ${S}/src/manifest -C build .
}

do_install_append() {
	install -d ${D}${bindir}

	install -m 0755 ${WORKDIR}/rhino ${D}${bindir}
	install -m 0755 ${WORKDIR}/rhino-jsc ${D}${bindir}
}

SRC_URI[md5sum] = "ad67a3dff135e3a70f0c3528a2d6edf2"
SRC_URI[sha256sum] = "9eb08f85bbe7c8e0b9eaffb1cf4984b31fb679f3c8a682acc3bb8ac20626c61e"
