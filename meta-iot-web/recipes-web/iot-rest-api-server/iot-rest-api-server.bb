DESCRIPTION = "Server for IOT REST APIs."
HOMEPAGE = "https://github.com/01org/iot-rest-api-server"
LICENSE = "Apache-2.0"

LIC_FILES_CHKSUM = "file://${WORKDIR}/git/LICENSE;md5=fa818a259cbed7ce8bc2a22d35a464fc"

DEPENDS = "nodejs-native iotivity iotivity-node"
RDEPENDS_${PN} += "bash iotivity-node iptables"

SRC_URI = "git://git@github.com/01org/iot-rest-api-server.git;protocol=https \
           file://0001-Remove-iotivity-node-dependency.patch \
           file://iot-rest-api-server.service \
           file://iot-rest-api-server.socket \
           file://${PN}-ipv4.conf \
           file://${PN}-ipv6.conf \
          "
SRCREV = "be42a70843cf0651ffd09c4c2913ceec4bf3f9fa"

S = "${WORKDIR}/git"

inherit systemd useradd

SYSTEMD_SERVICE_${PN} = "iot-rest-api-server.socket"

USERADD_PACKAGES = "${PN}"
GROUPADD_PARAM_${PN} = "-r restful"
USERADD_PARAM_${PN} = "\
--system --home ${localstatedir}/lib/empty \
--no-create-home --shell /bin/false \
--gid restful restful \
"

INSANE_SKIP_${PN} += "ldflags staticdev"

do_compile_prepend() {
    OCTBDIR="${STAGING_DIR_TARGET}${includedir}/iotivity/resource"
    export OCTBSTACK_CFLAGS="-I${OCTBDIR} -I${OCTBDIR}/stack -I${OCTBDIR}/logger -I${OCTBDIR}/oc_logger -I${OCTBDIR}/ocrandom -DROUTING_GATEWAY"
    export OCTBSTACK_LIBS="-loctbstack"
    export CFLAGS="$CFLAGS -fPIC"
    export CXXFLAGS="$CXXFLAGS -fPIC"
}

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
    install -d ${D}${libdir}/node_modules/iot-rest-api-server/
    cp -r ${S}/* ${D}${libdir}/node_modules/iot-rest-api-server/

    # Install iot-rest-api-server service script
    install -d ${D}/${systemd_unitdir}/system
    install -m 0644 ${WORKDIR}/iot-rest-api-server.service ${D}/${systemd_unitdir}/system/
    install -m 0644 ${WORKDIR}/iot-rest-api-server.socket ${D}/${systemd_unitdir}/system/

    # copy the firewall configuration fragments in place
    install -d ${D}${systemd_unitdir}/system/${PN}.socket.d
    install -m 0644 ${WORKDIR}/${PN}-ipv4.conf ${D}${systemd_unitdir}/system/${PN}.socket.d
    if ${@bb.utils.contains('DISTRO_FEATURES', 'ipv6', 'true', 'false', d)}; then
        install -m 0644 ${WORKDIR}/${PN}-ipv6.conf ${D}${systemd_unitdir}/system/${PN}.socket.d
    fi
}

FILES_${PN} = "${libdir}/node_modules/iot-rest-api-server/ \
               ${systemd_unitdir}/system/ \
               ${systemd_unitdir}/system/${PN}.socket.d/${PN}-ipv4.conf \
               ${@bb.utils.contains('DISTRO_FEATURES', 'ipv6', \
                   '${systemd_unitdir}/system/${PN}.socket.d/${PN}-ipv6.conf', '', d)} \
              "

INHIBIT_PACKAGE_DEBUG_SPLIT = "1"

PACKAGES = "${PN}"
