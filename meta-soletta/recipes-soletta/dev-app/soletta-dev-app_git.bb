DESCRIPTION = "Soletta Development Application"
RDEPENDS_${PN} = "soletta nodejs systemd graphviz libmicrohttpd avahi-daemon bash git"
LICENSE = "Apache-2.0"

PV = "1_beta10"

LIC_FILES_CHKSUM = "file://${S}/LICENSE;md5=93888867ace35ffec2c845ea90b2e16b"
SRC_URI[md5sum] = "00f1c0b970cc8d682c7a20c960f4b8e7"
SRC_URI[sha256sum] = "98ab16895a65692221035998a73d830b04a6835c672c9d64cac2010431519f8e"
SRC_URI = "https://github.com/solettaproject/soletta-dev-app/releases/download/v${PV}/soletta-dev-app_standalone_v${PV}.tar.gz;protocol=archive \
           file://soletta-dev-app.service \
           file://soletta-dev-app-mac.sh \
           file://soletta-dev-app-avahi-discover.service \
"

S = "${WORKDIR}/${PN}"

# We provide only one package
PACKAGES = " \
	${PN} \
"

inherit systemd

INSTALLATION_PATH = "/opt/"
SYSTEMD_PATH = "${systemd_unitdir}/system/"
AVAHI_SERVICE = "/etc/avahi/services/"

FILES_${PN} += " \
    ${INSTALLATION_PATH}soletta-dev-app \
    ${SYSTEMD_PATH}soletta-dev-app-server.service \
    ${SYSTEMD_PATH}fbp-runner@.service \
    ${AVAHI_SERVICE}soletta-dev-app.service \
    ${SYSTEMD_PATH}soletta-dev-app-avahi-discover.service \
    /soletta-dev-app/scripts/soletta-dev-app-mac.sh \
"

SYSTEMD_SERVICE_${PN} = "soletta-dev-app-server.service soletta-dev-app-avahi-discover.service"

SOLETTA_DEVAPP_INTERFACE ?= "enp2s0"

do_install() {
  install -d ${D}{INSTALLATION_PATH}
  install -d ${D}${INSTALLATION_PATH}soletta-dev-app
  cp -r ${S}/* ${D}${INSTALLATION_PATH}soletta-dev-app

  #SYSTEMD Installation part
  install -d ${D}${SYSTEMD_PATH}
  install -m 0664 ${S}/scripts/units/fbp-runner@.service ${D}${SYSTEMD_PATH}
  install -m 0664 ${S}/scripts/units/soletta-dev-app-server.service.in ${D}${SYSTEMD_PATH}soletta-dev-app-server.service
  sed -i "s@PATH@"${INSTALLATION_PATH}soletta-dev-app"@" ${D}${SYSTEMD_PATH}soletta-dev-app-server.service
  sed -i "s@"NODE_BIN_NAME"@"node"@" ${D}${SYSTEMD_PATH}soletta-dev-app-server.service

  #Configure avahi to discover Soletta Dev App server
  install -d ${D}${AVAHI_SERVICE}
  install -m 0664 ${WORKDIR}/soletta-dev-app.service ${D}${AVAHI_SERVICE}

  #Configure services that will set MAC address to Soletta Dev-App name
  install -m 0664 ${WORKDIR}/soletta-dev-app-avahi-discover.service ${D}${SYSTEMD_PATH}

 #Install set MAC address script
 install  -m 0755 ${WORKDIR}/soletta-dev-app-mac.sh ${D}${INSTALLATION_PATH}soletta-dev-app/scripts/
 sed -i -e 's/INTERFACE/${SOLETTA_DEVAPP_INTERFACE}/g' ${D}${INSTALLATION_PATH}soletta-dev-app/scripts/soletta-dev-app-mac.sh
}
