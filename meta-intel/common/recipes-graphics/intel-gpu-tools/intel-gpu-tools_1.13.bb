require ${COREBASE}/meta/recipes-graphics/xorg-app/xorg-app-common.inc

SUMMARY = "Intel GPU tools"
DESCRIPTION = "Variety of small tools for testing intel graphics."

LIC_FILES_CHKSUM = "file://COPYING;md5=0918806acfedc3e8c0488f2dd61616dd"

inherit autotools gtk-doc

DEPENDS += "libdrm libpciaccess cairo udev glib-2.0 libxv libx11 libxext libxrandr"
RDEPENDS_${PN} += "bash"
RDEPENDS_${PN}-tests += "bash"

PACKAGE_BEFORE_PN = "${PN}-benchmarks ${PN}-tests"

SRC_URI[md5sum] = "9ef0d6385e2665db7afa6432f1418ed3"
SRC_URI[sha256sum] = "c6e65884c106eff4af3a6896ae3fede6bf309337962f2e75ab897f116872ae34"

PACKAGECONFIG ??= ""
PACKAGECONFIG[libunwind] = "--with-libunwind,--without-libunwind,libunwind,libunwind"

EXTRA_OECONF = "--disable-nouveau --disable-shader-debugger"
COMPATIBLE_HOST = "(x86_64.*|i.86.*)-linux"

gputools_sysroot_preprocess() {
	rm -f ${SYSROOT_DESTDIR}${libdir}/pkgconfig/intel-gen4asm.pc
}
SYSROOT_PREPROCESS_FUNCS += "gputools_sysroot_preprocess"

FILES_${PN} += "${libdir}/intel_aubdump.so"
FILES_${PN}-benchmarks += "${libexecdir}/intel-gpu-tools/benchmarks"
FILES_${PN}-tests += "\
		${libexecdir}/intel-gpu-tools/*\
		${datadir}/intel-gpu-tools/1080p-right.png\
		${datadir}/intel-gpu-tools/1080p-left.png\
		${datadir}/intel-gpu-tools/pass.png\
		${datadir}/intel-gpu-tools/test-list.txt"
