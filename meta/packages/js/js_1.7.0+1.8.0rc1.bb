DESCRIPTION = "Spidermonkey: a javascript engine written in C"
HOMEPAGE = "http://www.mozilla.org/js/spidermonkey/"
SECTION = "libs"

# the package is licensed under either of the following
LICENSE = "MPL1.1 | GPLv2+ | LGPLv2.1+"
LIC_FILES_CHKSUM = "file://jsapi.c;beginline=4;endline=39;md5=347c6bbf4fb4547de1fa5ad830030063"
PR = "r1"

SRC_URI = "http://ftp.mozilla.org/pub/mozilla.org/js/js-1.8.0-rc1.tar.gz \
           file://link_with_gcc.patch \
           file://usepic.patch \
           file://buildcc.patch;striplevel=2 \
           file://jsautocfg.h \
           file://configure.ac"

S = "${WORKDIR}/js/src"

# use local autoconf script to generate a usable jsautocfg.h
# don't bother with automake
inherit autotools

do_configure_prepend() {
	cp -f ${WORKDIR}/configure.ac ${S}
	cp -f ${WORKDIR}/jsautocfg.h ${S}
}

EXTRA_OEMAKE = "'CC=${CC}' 'LD=${LD}' 'XCFLAGS=${CFLAGS}' 'XLDFLAGS=${LDFLAGS} -Wl,-soname=libjs' \
                'BUILD_CC=${BUILD_CC}' 'BUILD_CFLAGS=${BUILD_CFLAGS}' 'BUILD_LDFLAGS=${BUILD_LDFLAGS}'"

PARALLEL_MAKE = ""

do_compile() {
	oe_runmake -f Makefile.ref JS_EDITLINE=1 PREBUILT_CPUCFG=1 BUILD_OPT=1
}

do_install() {
	install -d ${D}${libdir}
	install -d ${D}${includedir}
	install -d ${D}${includedir}/js
	oe_libinstall -so -C Linux_All_OPT.OBJ libjs ${D}${libdir}
	install -m 0644 ${S}/*.h ${D}${includedir}/js
}

FILES_${PN} = "${libdir}/lib*.so"
FILES_${PN}-dev = "${includedir} ${libdir}/lib*.a"

