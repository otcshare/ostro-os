SUMMARY = "libcrypto* (OpenSSL*) QAT_MEM Memory Management Module \
for Intel Quick Assist Technology"
DESCRIPTION = "This software adds an engine that accelerates some of \
the libcrypto algorithms via the Intel QuickAssist Technology \
implemented on Intel Communications Chipset 89xx Series based platforms."

HOMEPAGE = "http://www.openssl.org/"
SECTION = "libs/network"
LICENSE = "openssl & GPLv2 & BSD"

LIC_FILES_CHKSUM = "file://${WORKDIR}/git/LICENSE;md5=f9a8f968107345e0b75aa8c2ecaa7ec8 \
                    file://${COMMON_LICENSE_DIR}/GPL-2.0;md5=801f80980d171dd6425610833a22dbe6 \
                    file://${COMMON_LICENSE_DIR}/BSD;md5=3775480a712fc46a69647678acb234cb \
                    "

SRC_URI  = "https://01.org/sites/default/files/page/libcrypto_shim_${PV}_withdocumentation.zip;name=openssl_qat;subdir=openssl_qat-${PV} \
            file://openssl_qat-environment-variables-to-have-precedence.patch \
            file://openssl_qat-pass-oe_ldflags-to-linker.patch \
            file://openssl_qat-remove-redundant-rpaths.patch \
            file://openssl_qat-build-qat_mem-ko-against-yocto-kernel.patch \
            file://openssl_qat-install-engines-in-libdir-ssl.patch \
            "

DEPENDS         += " qat16 zlib"
RDEPENDS_${PN}  += " qat16 zlib zlib-qat"

inherit pkgconfig module

PACKAGES =+ "${PN}-misc"
PARALLEL_MAKE = ""

AR_append = " r"
EXTRA_OEMAKE = "-e MAKEFLAGS="

export ICP_ROOT = "${WORKDIR}/git"
export ICP_BUILD_OUTPUT = "${STAGING_DIR_TARGET}"
export OPENSSL_ROOT = "${ICP_ROOT}"
export OPENSSL_PREFIX = "/usr/local"
export AS = "${CC} -c"
export OE_LDFLAGS="${LDFLAGS} -L${OPENSSL_PREFIX}{base_libdir}"
export ICP_API_PATH = "${STAGING_DIR_TARGET}${includedir}/lac"
export KERNEL_SOURCE_ROOT = "${STAGING_KERNEL_DIR}"
export KERNEL_BUILDDIR = "${STAGING_KERNEL_BUILDDIR}"

S = "${WORKDIR}/git"

opensslqat_do_patch() {
        cd ${WORKDIR}/openssl_qat-${PV}
        cd libcrypto_shim_${PV}_*
        tar -zxof libCrypto_Shim_${PV}.tar.gz
        tar -zxof libcrypto-openssl-${OPENSSL_VERSION}-qat.L.${PV}.tar.gz
        mv openssl-${OPENSSL_VERSION}-qat.patch ${WORKDIR}

	cd ${S}
        if [ ! -d ${S}/debian/patches ]; then
                mkdir -p ${S}/debian/patches
                cp -f ${WORKDIR}/openssl-${OPENSSL_VERSION}-qat.patch ${S}/debian/patches
                echo "openssl-${OPENSSL_VERSION}-qat.patch -p1" > ${S}/debian/patches/series
        fi
        quilt pop -a || true
        if [ -d ${S}/.pc-opensslqat ]; then
                rm -rf ${S}/.pc
                mv ${S}/.pc-opensslqat ${S}/.pc
                QUILT_PATCHES=${S}/debian/patches quilt pop -a
                rm -rf ${S}/.pc
        fi
        QUILT_PATCHES=${S}/debian/patches quilt push -a
        mv ${S}/.pc ${S}/.pc-opensslqat
}

# We invoke base do_patch at end, to incorporate any local patch
python do_patch() {
    bb.build.exec_func('opensslqat_do_patch', d)
    bb.build.exec_func('patch_do_patch', d)
}

do_configure () {
	os=linux
	target=linux-x86_64

	./Configure -no-ssl3 enable-hw-qat --prefix=$OPENSSL_PREFIX --openssldir="${OPENSSL_PREFIX}${base_libdir}/ssl" --libdir="${base_libdir}" $target
}

do_compile() {
	oe_runmake
}

do_install() {
	install -m 0755 -d ${D}${bindir} \
			${D}${OPENSSL_PREFIX}/include \
			${D}${sysconfdir}/openssl_conf

	oe_runmake INSTALL_PREFIX="${D}" install

	cp --dereference -R include/openssl ${D}${OPENSSL_PREFIX}/include

	cp ${WORKDIR}/openssl_qat-${PV}/libcrypto_shim_${PV}_withdocumentation/qat/config/dh895xcc/multi_process_optimized/* ${D}${sysconfdir}/openssl_conf/
}

FILES_${PN}-misc += "\
		${OPENSSL_PREFIX}${base_libdir}/ssl/misc \
		${bindir}/c_rehash \
		"

FILES_${PN}-dbg += "\
		${OPENSSL_PREFIX}${base_libdir}/ssl/engines/.debug \
		${OPENSSL_PREFIX}${base_libdir}/engines/.debug \
		${OPENSSL_PREFIX}${base_libdir}/.debug \
		${OPENSSL_PREFIX}/bin/.debug \
		"

FILES_${PN}-dev =  "${OPENSSL_PREFIX}/include"

FILES_${PN}-staticdev += "${OPENSSL_PREFIX}${base_libdir}/*.a"

FILES_${PN} =+ "\
		${bindir} \
		${sysconfdir}/openssl_conf \
		${OPENSSL_PREFIX}/bin \
		${OPENSSL_PREFIX}${base_libdir} \
		${OPENSSL_PREFIX}${base_libdir}/ssl \
		${OPENSSL_PREFIX}${base_libdir}/ssl/openssl.cnf \
		"
