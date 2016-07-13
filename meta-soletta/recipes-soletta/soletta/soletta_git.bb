#
# soletta.bb
#

DESCRIPTION = "Soletta library and modules"
SECTION = "examples"
DEPENDS = "glib-2.0 libpcre pkgconfig python3-jsonschema-native icu curl libmicrohttpd mosquitto nodejs nodejs-native"
DEPENDS += " ${@bb.utils.contains('DISTRO_FEATURES','systemd','systemd','',d)}"
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=93888867ace35ffec2c845ea90b2e16b"
PV = "1_beta19+git${SRCPV}"

SRC_URI = "gitsm://github.com/solettaproject/soletta.git;protocol=git \
           file://run-ptest \
           file://i2c-dev.conf \
           file://iio-trig-sysfs.conf \
          "
SRCREV = "6a7bc32376904ac385dea073cb8d71a74f2e8629"

S = "${WORKDIR}/git"

inherit cml1 python3native

PACKAGECONFIG ??= "${@bb.utils.contains('DISTRO_FEATURES','x11', 'x11', '', d)}"
PACKAGECONFIG[x11] = ",,cairo atk gtk+3 gdk-pixbuf pango,"

PACKAGES_prepend = " \
         ${PN}-nodejs \
         ${PN}-flow-gtk \
"

FILES_${PN}-dbg_append = " \
                  ${datadir}/gdb \
"

FILES_${PN}-dev_append = " \
                ${datadir}/soletta/* \
                ${includedir}/soletta/* \
                ${libdir}/pkgconfig/soletta.pc \
                ${libdir}/soletta/modules/flow/* \
                ${libdir}/soletta/modules/update/* \
                ${libdir}/soletta/modules/pin-mux/* \
                ${libdir}/soletta/modules/linux-micro/* \
                ${libdir}/soletta/modules/flow-metatype/* \
                ${sysconfdir}/modules-load.d/* \
"

ALLOW_EMPTY_${PN}-flow-gtk = "1"
FILES_${PN}-flow-gtk = " \
                ${libdir}/soletta/modules/flow/gtk.so \
                ${datadir}/soletta/flow/descriptions/gtk.json \
"
INSANE_SKIP_${PN}-flow-gtk += "dev-deps"

FILES_${PN} = " \
            ${bindir}/sol* \
            ${libdir}/libsoletta.so* \
            ${libdir}/soletta/soletta-image-hash \
"

FILES_${PN}-nodejs = " \
                   ${libdir}/node_modules/soletta \
"
INSANE_SKIP_${PN}-nodejs += "dev-deps"

# Setup what PACKAGES should be installed by default.
# If a package should not being installed, use BAD_RECOMMENDS.
RRECOMMENDS_${PN} = "\
                  ${PN} \
                  ${PN}-dev \
"

# since we only enable flow-module-udev only with systemd feature
# can can disable the RDEPENDS based on the same criteria
RDEPENDS_${PN} = " \
             ${@bb.utils.contains('DISTRO_FEATURES','systemd','libudev','',d)} \
             chrpath \
             libpcre \
"

# do_package_qa tells soletta rdepends on soletta-dev
# maybe an non-obvious implicit rule implied by yocto
INSANE_SKIP_${PN} += "dev-deps file-rdeps"
INSANE_SKIP_${PN}-dev += "dev-elf"

B = "${WORKDIR}/git"

do_configure_prepend() {
   export TARGETCC="${CC}"
   export TARGETAR="${AR}"
   export LIBDIR="${libdir}/"
}

do_configure_append() {
   # The RPATH should not be set otherwise it will set the path of the host
   # becoming invalid
   # Also, yocto has a toolchain that will treat RPATH for Soletta
   sed -i "s/^RPATH=y/# RPATH is not set/g" ${S}/.config

   if ${@bb.utils.contains('PACKAGECONFIG', 'x11', 'false', 'true', d)}; then
       sed -i -e 's/^ *FLOW_NODE_TYPE_GTK=.*/# FLOW_NODE_TYPE_GTK is not set/g' ${S}/.config
   fi

}

do_compile() {
   # changing the home directory to the working directory, the .npmrc will be created in this directory
   export HOME=${WORKDIR}
   export LIBDIR="${libdir}/"

   # Exported by python3native.bbclass as of OE-core c1e0eb62f2 and
   # breaks compilation of node-gyp because gyp only works with
   # Python2 (https://codereview.chromium.org/1454433002).
   unset PYTHON

   # does not build dev packages
   npm config set dev false

   # access npm registry using http
   npm set strict-ssl false
   npm config set registry http://registry.npmjs.org/

   # configure http proxy if necessary
   if [ -n "${http_proxy}" ]; then
       npm config set proxy ${http_proxy}
       NODE_GYP_PROXY="--proxy=${http_proxy}"
   fi
   if [ -n "${HTTP_PROXY}" ]; then
       npm config set proxy ${HTTP_PROXY}
       NODE_GYP_PROXY="--proxy=${HTTP_PROXY}"
   fi

   # configure cache to be in working directory
   npm set cache ${WORKDIR}/npm_cache

   # clear local cache prior to each compile
   npm cache clear

   case ${TARGET_ARCH} in
       i?86) targetArch="ia32"
           ;;
       x86_64) targetArch="x64"
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

   # Export needed variables to build Node.js bindings
   export CFLAGS="$CFLAGS -fPIC"
   export CXXFLAGS="$CXXFLAGS -fPIC"
   export NODE_GYP="${STAGING_DIR_TARGET}/${libdir}/node_modules/npm/bin/node-gyp-bin/node-gyp --arch=${targetArch} ${NODE_GYP_PROXY}"

   oe_runmake CFLAGS="--sysroot=${STAGING_DIR_TARGET} -pthread -lpcre" TARGETCC="${CC}" TARGETAR="${AR}"
}

do_install() {
   export LIBDIR="${libdir}/"
   oe_runmake DESTDIR=${WORKDIR}/image install CFLAGS="--sysroot=${STAGING_DIR_TARGET}" TARGETCC="${CC}" TARGETAR="${AR}"
   unlink ${WORKDIR}/image/${libdir}/libsoletta.so
   mv ${WORKDIR}/image/${libdir}/libsoletta.so.0.0.1 ${WORKDIR}/image/${libdir}/libsoletta.so
   ln -sf libsoletta.so ${WORKDIR}/image/${libdir}/libsoletta.so.0.0.1
   COMMIT_ID=`git --git-dir=${WORKDIR}/git/.git rev-parse --verify HEAD`
   echo "Soletta: $COMMIT_ID" > ${D}/${libdir}/soletta/soletta-image-hash

   # Remove nan module as it is not needed.
   rm -rf ${WORKDIR}/image/${libdir}/node_modules/soletta/node_modules/nan
}

do_install_append() {
   install -d ${D}${sysconfdir}/modules-load.d
   install -m 0644 ${WORKDIR}/i2c-dev.conf ${D}${sysconfdir}/modules-load.d
   install -m 0644 ${WORKDIR}/iio-trig-sysfs.conf ${D}${sysconfdir}/modules-load.d
}

inherit ptest

do_compile_ptest() {
        export LIBDIR="${libdir}/"
        oe_runmake TARGETCC="${CC}" TARGETAR="${AR}" "tests"
}

do_install_ptest () {
        mkdir -p ${D}/${PTEST_PATH}/src
        cp -rf ${S}/build/stage/test ${D}/${PTEST_PATH}/src/
        cp -f ${S}/data/scripts/suite.py ${D}/${PTEST_PATH}
        cp -rf ${S}/src/test-fbp ${D}/${PTEST_PATH}/src/
        cp -f ${S}/tools/run-fbp-tests ${D}/${PTEST_PATH}

}

INSANE_SKIP_${PN}-ptest += "dev-deps"
