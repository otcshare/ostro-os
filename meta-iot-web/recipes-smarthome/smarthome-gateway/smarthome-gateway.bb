SUMMARY = "SmartHome Gateway"
DESCRIPTION = "SmartHome webserver running on the home gateway"
HOMEPAGE = "https://github.com/01org/SmartHome-Demo/"
LICENSE = "Apache-2.0"

LIC_FILES_CHKSUM = "file://COPYING;md5=82d0338d6e61d25fb51cabb1504c0df6"

DEPENDS = "nodejs-native iotivity iotivity-node"
RDEPENDS_${PN} += "iotivity node-mraa nodejs iotivity-node iptables"

SRC_URI = "git://git@github.com/01org/SmartHome-Demo.git;protocol=https \
           file://0001-Remove-iotivity-node-dependency.patch \
           file://smarthome-gateway.service \
           file://smarthome-gateway.socket \
           file://${PN}-ipv4.conf \
           file://${PN}-ipv6.conf \
           file://smarthome-power.service \
          "

SRCREV = "a7a6e745fad9485b2b7e8f650dbefa53f22aa11f"
PV = "0.1+git${SRCPV}"

S = "${WORKDIR}/git/"

inherit systemd
SYSTEMD_SERVICE_${PN} = "smarthome-gateway.socket \
                         smarthome-power.service \
                        "
INSANE_SKIP_${PN} += "ldflags staticdev"

POWER_INSTALLATION_PATH = "/opt/smarthome-ocf-servers"

do_compile () {
    # changing the home directory to the working directory, the .npmrc will be created in this directory
    export HOME=${WORKDIR}

    # does not build dev packages
    npm config set dev false

    # access npm registry using http
    npm set strict-ssl false
    npm config set registry http://registry.npmjs.org/

    # configure http proxy if neccessary
    if [ -n "${http_proxy}" ]; then
        npm config set proxy ${http_proxy}
    fi
    if [ -n "${HTTP_PROXY}" ]; then
        npm config set proxy ${HTTP_PROXY}
    fi

    # configure cache to be in working directory
    npm set cache ${WORKDIR}/npm_cache

    # clear local cache prior to each compile
    npm cache clear

    case ${TARGET_ARCH} in
        i?86) targetArch="ia32"
            echo "targetArch = 32"
            ;;
        x86_64) targetArch="x64"
            echo "targetArch = 64"
            ;;
        arm) targetArch="arm"
            ;;
        mips) targetArch="mips"
            ;;
        sparc) targetArch="sparc"
            ;;
        *) echo "unknown architecture"
           exit 1
            ;;
    esac

    # Compile and install node modules in source directory
    npm --arch=${targetArch} --production --verbose install
}

do_install () {
    install -d ${D}${libdir}/node_modules/smarthome-gateway/

    install -m 0644 ${S}/first_server.js ${D}${libdir}/node_modules/smarthome-gateway/first_server.js
    install -m 0644 ${S}/data.json ${D}${libdir}/node_modules/smarthome-gateway/data.json
    install -m 0644 ${S}/package.json ${D}${libdir}/node_modules/smarthome-gateway/package.json

    cp -r ${S}/gateway-webui/ ${D}${libdir}/node_modules/smarthome-gateway/
    cp -r ${S}/node_modules/ ${D}${libdir}/node_modules/smarthome-gateway/

    # Install SmartHome Power sensor
    install -d ${D}${POWER_INSTALLATION_PATH}
    install -m 0664 ${S}/ocf-servers/js-servers/power-uart.js ${D}${POWER_INSTALLATION_PATH}/smarthome-power.js

    # Install SmartHome Power service script
    install -d ${D}/${systemd_unitdir}/system
    install -m 0644 ${WORKDIR}/smarthome-power.service ${D}/${systemd_unitdir}/system/

    # Install SmartHome gateway service script
    install -d ${D}/${systemd_unitdir}/system
    install -m 0644 ${WORKDIR}/smarthome-gateway.service ${D}/${systemd_unitdir}/system/
    install -m 0644 ${WORKDIR}/smarthome-gateway.socket ${D}/${systemd_unitdir}/system/

    # Copy the firewall configuration fragments in place
    install -d ${D}${systemd_unitdir}/system/${PN}.socket.d
    install -m 0644 ${WORKDIR}/${PN}-ipv4.conf ${D}${systemd_unitdir}/system/${PN}.socket.d
    if ${@bb.utils.contains('DISTRO_FEATURES', 'ipv6', 'true', 'false', d)}; then
        install -m 0644 ${WORKDIR}/${PN}-ipv6.conf ${D}${systemd_unitdir}/system/${PN}.socket.d
    fi

}

FILES_${PN} = "${libdir}/node_modules/smarthome-gateway/ \
               ${POWER_INSTALLATION_PATH} \
               ${systemd_unitdir}/system/ \
               ${systemd_unitdir}/system/${PN}.socket.d/${PN}-ipv4.conf \
               ${@bb.utils.contains('DISTRO_FEATURES', 'ipv6', \
                   '${systemd_unitdir}/system/${PN}.socket.d/${PN}-ipv6.conf', '', d)} \
              "

INHIBIT_PACKAGE_DEBUG_SPLIT = "1"

PACKAGES = "${PN}"
