SUMMARY = "OCF Fan sensor"
DESCRIPTION = "OCF Fan sensor server for SmartHome demo"
HOMEPAGE = "https://github.com/01org/SmartHome-Demo/"
LICENSE = "Apache-2.0"

LIC_FILES_CHKSUM = "file://COPYING;md5=82d0338d6e61d25fb51cabb1504c0df6"

RDEPENDS_${PN} += "iotivity node-mraa nodejs iotivity-node"

SRC_URI = "git://git@github.com/01org/SmartHome-Demo.git;protocol=https \
           file://smarthome-fan.service \
          "
SRCREV = "a7a6e745fad9485b2b7e8f650dbefa53f22aa11f"
PV = "0.1+git${SRCPV}"

S = "${WORKDIR}/git/"

INSTALLATION_PATH = "/opt/smarthome-ocf-servers"
inherit systemd
SYSTEMD_SERVICE_${PN} = "smarthome-fan.service"

do_install() {
    install -d ${D}${INSTALLATION_PATH}
    install -m 0664 ${S}/ocf-servers/js-servers/fan.js ${D}${INSTALLATION_PATH}/smarthome-fan.js

    # Install SmartHome fan service script
    install -d ${D}/${systemd_unitdir}/system
    install -m 0644 ${WORKDIR}/smarthome-fan.service ${D}/${systemd_unitdir}/system/
}

FILES_${PN} = "${INSTALLATION_PATH} \
               ${systemd_unitdir}/system/ \
              "

PACKAGES = "${PN}"
