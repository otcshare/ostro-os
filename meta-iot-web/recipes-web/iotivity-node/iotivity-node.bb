DESCRIPTION = "This project provides iotivity node.js bindings."
HOMEPAGE = "https://github.com/otcshare/iotivity-node"
LICENSE = "MIT"

LIC_FILES_CHKSUM = "file://${WORKDIR}/git/MIT-LICENSE.txt;md5=6b58eb710e76f8b9795f41edf589db99"

DEPENDS = "nodejs-native glib-2.0 iotivity"
RDEPENDS_${PN} += "bash iotivity-resource"

SRC_URI = "git://github.com/otcshare/iotivity-node.git;protocol=https"
SRCREV = "38f76790e2d0f4960b0f3360c7bbcdf5a69907f4"

S = "${WORKDIR}/git"
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
    install -d ${D}${libdir}/node_modules/iotivity-node/
    install -m 0644 ${S}/AUTHORS.txt ${D}${libdir}/node_modules/iotivity-node/AUTHORS.txt
    install -m 0644 ${S}/index.js ${D}${libdir}/node_modules/iotivity-node/index.js
    install -m 0644 ${S}/lowlevel.js ${D}${libdir}/node_modules/iotivity-node/lowlevel.js
    install -m 0644 ${S}/MIT-LICENSE.txt ${D}${libdir}/node_modules/iotivity-node/MIT-LICENSE.txt
    install -m 0644 ${S}/README.md ${D}${libdir}/node_modules/iotivity-node/README.md

    cp -r ${S}/lib/ ${D}${libdir}/node_modules/iotivity-node/
    cp -r ${S}/node_modules/ ${D}${libdir}/node_modules/iotivity-node/

    install -d ${D}${libdir}/node_modules/iotivity-node/build/Release/
    install -m 0755 ${S}/build/Release/iotivity.node ${D}${libdir}/node_modules/iotivity-node/build/Release/
}

FILES_${PN} = "${libdir}/node_modules/iotivity-node/ \
"

INHIBIT_PACKAGE_DEBUG_SPLIT = "1"

PACKAGES = "${PN}"
