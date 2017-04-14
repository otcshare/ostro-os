DESCRIPTION = "Intel(r) Data Plane Development Kit"
HOMEPAGE = "http://dpdk.org"
LICENSE = "BSD & LGPLv2 & GPLv2"
LIC_FILES_CHKSUM = "file://LICENSE.GPL;md5=751419260aa954499f7abaabaa882bbe"

SRC_URI = "http://fast.dpdk.org/rel/${BP}.tar.gz;name=dpdk \
	   file://dpdk-16.04-add-RTE_KERNELDIR_OUT-to-split-kernel-bu.patch \
	   file://dpdk-16.07-add-sysroot-option-within-app-makefile.patch \
	   file://dpdk-16.04-point-to-the-right-include-and-lib-path.patch \
	   file://dpdk-16.04-Fix-for-misleading-indentation-error.patch \
	   file://dpdk-16.04-dpdk-fix-compilation-with-dynamic-libs.patch \
	   file://dpdk-16.07-dpdk-fix-for-parellel-make-issue.patch \
	   file://dpdk-17.02-dpdk-fix-installation-warning-and-issue.patch \
	  "

COMPATIBLE_MACHINE = "intel-corei7-64"

# dpdk example apps dpdk_qat and vhost have dependancy on fuse and qat.
# fuse is in meta-filesystems and qat is not yet upstreamed.
# So adding mechanism to explicitly disable the use of fuse and qat.
# To enable, uncomment the below line or include in .bbappend.
# PACKAGECONFIG ?= " dpdk_qat vhost libvirt"

PACKAGECONFIG[dpdk_qat] = ",,virtual/qat"
PACKAGECONFIG[vhost] = ",,fuse"
PACKAGECONFIG[libvirt] = ",,libvirt"

export CONFIG_EXAMPLE_DPDK_QAT = "${@bb.utils.contains('PACKAGECONFIG', 'dpdk_qat', 'y', 'n', d)}"
export CONFIG_EXAMPLE_VM_POWER_MANAGER = "${@bb.utils.contains('PACKAGECONFIG', 'libvirt', 'y', 'n', d)}"
export CONFIG_VHOST_ENABLED = "${@bb.utils.contains('PACKAGECONFIG', 'vhost', 'y', 'n', d)}"

RDEPENDS_${PN} += "python-subprocess dpdk-dev-libibverbs"
DEPENDS = "virtual/kernel dpdk-dev-libibverbs"
do_configure[depends] += "virtual/kernel:do_shared_workdir"

inherit module

export MODULE_DIR="/lib/modules/${KERNEL_VERSION}/kernel/drivers/net"
export RTE_SDK = "${S}"
export RTE_TARGET="${@bb.utils.contains("TUNE_FEATURES", "corei7", "x86_64-native-linuxapp-gcc", "i686-native-linuxapp-gcc", d)}"

export ICP_ROOT = "${PKG_CONFIG_SYSROOT_DIR}/usr/include"
export ICP_LIB_ROOT= "${PKG_CONFIG_SYSROOT_DIR}/usr/lib"
export RTE_KERNELDIR = "${STAGING_KERNEL_DIR}"
export RTE_KERNELDIR_OUT = "${STAGING_KERNEL_BUILDDIR}"
export INSTALL_PATH = "${prefix}/share"
export RTE_OUTPUT = "${S}/${RTE_TARGET}"
export ETHTOOL_LIB_PATH = "${S}/examples/ethtool/lib/${RTE_TARGET}/"
export SYSROOTPATH = "--sysroot=${STAGING_DIR_HOST}"
export DPDK_TARGET_MACH = "${@get_dpdk_target_mach(bb,d)}"
export ICP_LAC_API_DIR = "${STAGING_DIR_TARGET}${includedir}/lac"

# The list of intel Comms platforms and their target machine
# process mapping. The supported target machine is listed under
# dpdk/mk/machine
def get_dpdk_target_mach(bb, d):
    target_arch = d.getVar('MACHINE_ARCH', True)
    multiarch_options = {
        "mohonpeak64":    "atm",
        "mohonpeak32":    "atm",
        "crystalforest":  "ivb",
        "intel_corei7_64": "hsw",
    }

    if target_arch in multiarch_options :
            return multiarch_options[target_arch]
    return ""

do_configure () {
	#############################################################
	### default value for prefix is "usr", unsetting it, so it
	### will not be concatenated in ${RTE_TARGET}/Makefile
	### which will cause compilation failure
	#############################################################
	unset prefix

	# Fix-up CONFIG_RTE_MACHINE based on target machine
	sed -e "s#CONFIG_RTE_MACHINE=\"native\"#CONFIG_RTE_MACHINE=\"${DPDK_TARGET_MACH}\"#" -i ${S}/config/defconfig_x86_64-native-linuxapp-gcc
	sed -e "s#CONFIG_RTE_MACHINE=\"native\"#CONFIG_RTE_MACHINE=\"${DPDK_TARGET_MACH}\"#" -i ${S}/config/defconfig_i686-native-linuxapp-gcc

	# Fix-up vhost configs based on package config
	sed -e "s#CONFIG_RTE_KNI_VHOST=n#CONFIG_RTE_KNI_VHOST=${CONFIG_VHOST_ENABLED}#" -i ${S}/config/common_linuxapp
	sed -e "s#CONFIG_RTE_KNI_VHOST_VNET_HDR_EN=n#CONFIG_RTE_KNI_VHOST_VNET_HDR_EN=${CONFIG_VHOST_ENABLED}#" -i ${S}/config/common_linuxapp
	sed -e "s#CONFIG_RTE_LIBRTE_VHOST=n#CONFIG_RTE_LIBRTE_VHOST=${CONFIG_VHOST_ENABLED}#" -i ${S}/config/common_linuxapp

	make O=$RTE_TARGET T=$RTE_TARGET config
}

do_compile () {
	unset LDFLAGS TARGET_LDFLAGS BUILD_LDFLAGS

	cd ${S}/${RTE_TARGET}
	oe_runmake EXTRA_LDFLAGS="-L${STAGING_LIBDIR} --hash-style=gnu" \
		   EXTRA_CFLAGS="--sysroot=${STAGING_DIR_HOST} -I${STAGING_INCDIR}" \
		   CROSS="${TARGET_PREFIX}" \
		   prefix=""  LDFLAGS=""  WERROR_FLAGS="-w" V=1

	cd ${S}/examples/
	oe_runmake EXTRA_LDFLAGS="-L${STAGING_LIBDIR} --hash-style=gnu" \
		   EXTRA_CFLAGS="--sysroot=${STAGING_DIR_HOST} -I${STAGING_INCDIR}" \
		   CROSS="${TARGET_PREFIX}" O="${S}/examples/$@/"
}

do_install () {
	oe_runmake O=${RTE_OUTPUT} T= install-runtime DESTDIR=${D}
	oe_runmake O=${RTE_OUTPUT} T= install-kmod DESTDIR=${D} kerneldir=${MODULE_DIR}
	oe_runmake O=${RTE_OUTPUT} T= install-sdk DESTDIR=${D}

	# Install examples
	for dirname in ${S}/examples/*
	do
		install -m 0755 -d ${D}/${INSTALL_PATH}/examples/`basename ${dirname}`

		for appname in `find ${dirname} -regex ".*${EXAMPLES_BUILD_DIR}\/app\/[-0-9a-zA-Z0-9/_]*$"`
		do
			install -m 755 ${appname}	${D}/${INSTALL_PATH}/examples/`basename ${dirname}`/
		done
	done
}

PACKAGES += "${PN}-examples"

FILES_${PN}-dbg += " \
	${INSTALL_PATH}/.debug \
	${INSTALL_PATH}/examples/*/.debug \
	"

FILES_${PN}-doc += "\
	${INSTALL_PATH}/doc \
	"

FILES_${PN}-dev += " \
	${INSTALL_PATH}/${RTE_TARGET}/.config \
	${includedir} \
	${includedir}/${ARCHDIR} \
	${includedir}/exec-env \
	${INSTALL_PATH}/buildtools/ \
	${INSTALL_PATH}/${RTE_TARGET}/include \
	${INSTALL_PATH}/${RTE_TARGET}/lib \
	"

FILES_${PN} += " ${INSTALL_PATH}/usertools/ \
		 ${prefix}/sbin/ \
		 ${prefix}/bin/ \
		 ${libdir}/ \
		 "
FILES_${PN}-examples += " \
	${INSTALL_PATH}/examples/* \
	"
