SUMMARY = "OCF servers"
DESCRIPTION = "Motion, Gas, Buzzer, LED, Illuminance, RGB LED and Temperature OCF servers for SmartHome demo"
HOMEPAGE = "https://github.com/01org/SmartHome-Demo/"
LICENSE = "Apache-2.0"

LIC_FILES_CHKSUM = "file://COPYING;md5=82d0338d6e61d25fb51cabb1504c0df6"

RDEPENDS_${PN} += "iotivity node-mraa nodejs node-upm iotivity-node"

SRC_URI = "git://git@github.com/01org/SmartHome-Demo.git;protocol=https \
           file://smarthome-motion.service \
           file://smarthome-gas.service \
           file://smarthome-led.service \
           file://smarthome-rgbled.service \
           file://smarthome-button-toggle.service \
           file://smarthome-illuminance.service \
           file://smarthome-buzzer.service \
           file://smarthome-temperature.service \
          "

SRCREV = "a7a6e745fad9485b2b7e8f650dbefa53f22aa11f"
PV = "0.1+git${SRCPV}"

S = "${WORKDIR}/git/"

INSTALLATION_PATH = "/opt/smarthome-ocf-servers"

inherit systemd
SYSTEMD_SERVICE_${PN} = "smarthome-motion.service \
                         smarthome-gas.service \
                         smarthome-led.service \
                         smarthome-rgbled.service \
                         smarthome-button-toggle.service \
                         smarthome-illuminance.service \
                         smarthome-buzzer.service \
                         smarthome-temperature.service \
                        "
do_install() {
    install -d ${D}${INSTALLATION_PATH}
    install -m 0664 ${S}/ocf-servers/js-servers/ambient_light.js ${D}${INSTALLATION_PATH}/smarthome-illuminance.js
    install -m 0664 ${S}/ocf-servers/js-servers/motion.js ${D}${INSTALLATION_PATH}/smarthome-motion.js
    install -m 0664 ${S}/ocf-servers/js-servers/gas.js ${D}${INSTALLATION_PATH}/smarthome-gas.js
    install -m 0664 ${S}/ocf-servers/js-servers/led.js ${D}${INSTALLATION_PATH}/smarthome-led.js
    install -m 0664 ${S}/ocf-servers/js-servers/temperature.js ${D}${INSTALLATION_PATH}/smarthome-temperature.js
    install -m 0664 ${S}/ocf-servers/js-servers/rgb_led.js ${D}${INSTALLATION_PATH}/smarthome-rgbled.js
    install -m 0664 ${S}/ocf-servers/js-servers/button-toggle.js ${D}${INSTALLATION_PATH}/smarthome-button-toggle.js
    install -m 0664 ${S}/ocf-servers/js-servers/buzzer.js ${D}${INSTALLATION_PATH}/smarthome-buzzer.js

    # Install SmartHome sensors service scripts
    install -d ${D}/${systemd_unitdir}/system
    install -m 0644 ${WORKDIR}/*.service ${D}/${systemd_unitdir}/system/
}

FILES_${PN} = "${INSTALLATION_PATH} \
               ${systemd_unitdir}/system/ \
              "

PACKAGES = "${PN}"
