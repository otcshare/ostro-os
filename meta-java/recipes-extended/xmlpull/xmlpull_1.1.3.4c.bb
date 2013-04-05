DESCRIPTION = "XML pull parser API"
HOMEPAGE = "http://www.xmlpull.org"
PRIORITY = "optional"
SECTION = "libs"
LICENSE = "PD"
LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=f353e5a2416136a69a4a44ed3b761f65"

DEPENDS = "ant-native"

inherit java-library

S = "${WORKDIR}/${PN}_1_1_3_4c"

JAR = "${PN}-${PV}.jar"

SRC_URI = "\
    http://www.extreme.indiana.edu/xmlpull-website/v1/download/xmlpull_1_1_3_4c_src.tgz \
    "

do_compile() {
    ANT_OPTS="-Dfile.encoding=iso-8859-1" ant
}

do_install() {
    cp build/lib/${PN}_1_1_3_4c.jar ${JAR}
}

SRC_URI[md5sum] = "34c8a093e5678dd633411dfea88f8558"
SRC_URI[sha256sum] = "e17aa1a26119966258a3656a262bbba0f0b036eecb6d9bf192cf4b497686f4c3"

