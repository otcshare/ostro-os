SUMMARY = "OCF Solar Panel sensor"
DESCRIPTION = "OCF Solar Panel sensor server for SmartHome demo"
HOMEPAGE = "https://github.com/01org/SmartHome-Demo/"
LICENSE = "Apache-2.0"

LIC_FILES_CHKSUM = "file://COPYING;md5=82d0338d6e61d25fb51cabb1504c0df6"

RDEPENDS_${PN} += "iotivity node-mraa nodejs node-upm iotivity-node"

SRC_URI = "git://git@github.com/01org/SmartHome-Demo.git;protocol=https \
           file://smarthome-solar.service \
          "
SRCREV = "a7a6e745fad9485b2b7e8f650dbefa53f22aa11f"
PV = "0.1+git${SRCPV}"

S = "${WORKDIR}/git/"

INSTALLATION_PATH = "/opt/smarthome-ocf-servers"

inherit systemd
SYSTEMD_SERVICE_${PN} = "smarthome-solar.service"

do_install() {
    install -d ${D}${INSTALLATION_PATH}
    install -m 0664 ${S}/ocf-servers/js-servers/solar.js ${D}${INSTALLATION_PATH}/smarthome-solar.js

    # Install SmartHome Solar service script
    install -d ${D}/${systemd_unitdir}/system
    install -m 0644 ${WORKDIR}/smarthome-solar.service ${D}/${systemd_unitdir}/system/
}

FILES_${PN} = "${INSTALLATION_PATH} \
               ${systemd_unitdir}/system/ \
              "

PACKAGES = "${PN}"
