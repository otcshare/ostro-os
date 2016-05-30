DESCRIPTION = "Soletta Development Application"
RDEPENDS_${PN} = "soletta nodejs systemd graphviz libmicrohttpd avahi-daemon bash git"
LICENSE = "Apache-2.0"

PV = "1_beta9"

LIC_FILES_CHKSUM = "file://${S}/LICENSE;md5=93888867ace35ffec2c845ea90b2e16b"
SRC_URI[md5sum] = "d6a08e58d14d4dd46fd7d5c27811132f"
SRC_URI[sha256sum] = "13f9829758e500d6de9215cc459be4f3953153a486dc8ce8c0aba8e3ee161e64"
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
}
