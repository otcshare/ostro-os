SUMMARY = "Iotivity Simple Client"
DESCRIPTION = "Iotivity Simple Client example which talks to the Simple Server example."
HOMEPAGE = "https://www.iotivity.org/"
DEPENDS = "iotivity"
SECTION = "apps"
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://simpleclient.cpp;beginline=1;endline=19;md5=fc5a615cf1dc3880967127bc853b3e0c"

SRC_URI = "file://iotivity-simple-client.tar.bz2 \
        file://0001-build-Use-LDFLAGS-variable-from-env.patch \
        "

S = "${WORKDIR}/iotivity-simple-client"

IOTIVITY_BIN_DIR = "/opt/iotivity"
IOTIVITY_BIN_DIR_D = "${D}${IOTIVITY_BIN_DIR}"

do_install() {
    install -d ${IOTIVITY_BIN_DIR_D}/apps/iotivity-simple-client
    install -c -m 555 ${S}/simpleclient ${IOTIVITY_BIN_DIR_D}/apps/iotivity-simple-client
    install -c -m 444 ${S}/oic_svr_db_client.dat ${IOTIVITY_BIN_DIR_D}/apps/iotivity-simple-client
}

FILES_${PN} = "${IOTIVITY_BIN_DIR}/apps/iotivity-simple-client/simpleclient \
               ${IOTIVITY_BIN_DIR}/apps/iotivity-simple-client/oic_svr_db_client.dat"
FILES_${PN}-dbg = "${IOTIVITY_BIN_DIR}/apps/iotivity-simple-client/.debug"
RDEPENDS_${PN} += "iotivity-resource"
BBCLASSEXTEND = "native nativesdk"

