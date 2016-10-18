DESCRIPTION = "Intel(r) QuickAssist Technology API"
HOMEPAGE = "https://01.org/packet-processing/intel%C2%AE-quickassist-technology-drivers-and-patches"

#Dual BSD and GPLv2 License
LICENSE = "BSD & GPLv2"
LIC_FILES_CHKSUM = "\
                    file://${COMMON_LICENSE_DIR}/GPL-2.0;md5=801f80980d171dd6425610833a22dbe6 \
                    file://${COMMON_LICENSE_DIR}/BSD;md5=3775480a712fc46a69647678acb234cb \
                    "

DEPENDS += "zlib openssl"
PROVIDES += "virtual/qat"

SRC_URI="file://qat16_2.3.0-34-qat-fix-for-cross-compilation-issue.patch \
         file://qat16_2.3.0-34-qat-remove-local-path-from-makefile.patch \
         file://qat16_2.3.0-34-make-sure-CFLAGS-are-correct.patch \
         file://qat16_2.5.0-80-qat-change-in-return-type-of-func-in-kernel-v4.4.patch \
         file://qat16_2.5.0-80-qat-Added-include-dir-path.patch \
         "

COMPATIBLE_MACHINE = "crystalforest|intel-corei7-64"

S = "${WORKDIR}/${ICP_DRIVER_TYPE}"
ICP_TOOLS = "accelcomp"
SAMPLE_CODE_DIR = "${S}/quickassist/lookaside/access_layer/src/sample_code"
TARGET_CC_ARCH += "$(LDFLAGS)"

export ICP_DRIVER_TYPE = "QAT1.6"
export ICP_FIRMWARE_DIR="dh895xcc"
export ICP_ROOT = "${S}"
export ICP_ENV_DIR = "${S}/quickassist/build_system/build_files/env_files"
export ICP_BUILDSYSTEM_PATH = "${S}/quickassist/build_system"
export ICP_TOOLS_TARGET = "${ICP_TOOLS}"
export FUNC_PATH = "${ICP_ROOT}/quickassist/lookaside/access_layer/src/sample_code/functional"
export KERNEL_SOURCE_ROOT = "${STAGING_KERNEL_DIR}"
export ICP_BUILD_OUTPUT = "${D}"
export DEST_LIBDIR = "${libdir}"
export DEST_BINDIR = "${bindir}"
export QAT_KERNEL_VER = "${KERNEL_VERSION}"
export SAMPLE_BUILD_OUTPUT = "${D}"
export MODULE_DIR = "${base_libdir}/modules/${KERNEL_VERSION}/kernel/drivers"

inherit module
inherit update-rc.d
INITSCRIPT_NAME = "qat_service"

PARALLEL_MAKE = ""

#To get around the double slashes in paths in QAT makefiles
PACKAGE_DEBUG_SPLIT_STYLE = "debug-without-src"

EXTRA_OEMAKE_append = " CFLAGS+='-fgnu89-inline -fPIC'"
EXTRA_OEMAKE = "-e MAKEFLAGS="
do_unpack2() {
        cd ${S}/
        tar xzvf ${ICP_DRIVER_TYPE}.L.${PV}.tar.gz
}

addtask unpack2 after do_unpack before do_patch

do_compile () {
        export LD="${LD} --hash-style=gnu"
        export MACHINE="${TARGET_ARCH}"
        cd ${S}/quickassist
        oe_runmake

        cd ${SAMPLE_CODE_DIR}
        touch ${SAMPLE_CODE_DIR}/performance/compression/calgary
        touch ${SAMPLE_CODE_DIR}/performance/compression/canterbury
       
        #build the whole sample code: fips, functional, performance
        oe_runmake 'all'
        oe_runmake 'fips_user_code'
}

do_install() {
        export MACHINE="${TARGET_ARCH}"
        cd ${S}/quickassist
        oe_runmake install

        cd ${SAMPLE_CODE_DIR}
        oe_runmake install

        install -d ${D}/etc/udev/rules.d \
                   ${D}${includedir} \
                   ${D}${includedir}/dc \
                   ${D}${includedir}/lac \
                   ${D}${sysconfdir}/dh895xcc \
                   ${D}${base_libdir}/firmware

        echo 'KERNEL=="icp_adf_ctl" MODE="0600"' > ${D}/etc/udev/rules.d/00-dh895xcc_qa.rules
        echo 'KERNEL=="icp_dev[0-9]*" MODE="0600"' >> ${D}/etc/udev/rules.d/00-dh895xcc_qa.rules
        echo 'KERNEL=="icp_dev_mem?" MODE="0600"' >> ${D}/etc/udev/rules.d/00-dh895xcc_qa.rules

        install -m 640 ${S}/quickassist/include/*.h ${D}${includedir}
        install -m 640 ${S}/quickassist/include/dc/*.h ${D}${includedir}/dc/
        install -m 640 ${S}/quickassist/include/lac/*.h ${D}${includedir}/lac/
        install -m 640 ${S}/quickassist/lookaside/access_layer/include/*.h ${D}${includedir}

        install -m 0755 ${SAMPLE_CODE_DIR}/performance/compression/calgary     ${D}${base_libdir}/firmware
        install -m 0755 ${SAMPLE_CODE_DIR}/performance/compression/canterbury  ${D}${base_libdir}/firmware

        install -m 660  ${S}/quickassist/config/dh* ${D}${sysconfdir}/dh895xcc
}

PACKAGES += "${PN}-app"

FILES_${PN}-dev = "${includedir}"

FILES_${PN} += "\
                ${base_libdir}/firmware/    \
                ${sysconfdir}/              \
                ${sysconfdir}/udev/rules.d/ \
                ${sysconfdir}/init.d/       \
                ${libdir}/                  \
                "

FILES_${PN}-dbg += "${sysconfdir}/init.d/.debug"

FILES_${PN}-app += "${bindir}/*"
