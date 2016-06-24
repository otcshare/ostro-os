SUMMARY = "Linux Key Management Utilities"
DESCRIPTION = "Keyutils is a set of utilities for managing the key retention \
facility in the kernel, which can be used by filesystems, block devices and \
more to gain and retain the authorization and encryption keys required to \
perform secure operations."
SECTION = "base"
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://LICENCE.GPL;md5=5f6e72824f5da505c1f4a7197f004b45"

PR = "r1"

SRCREV = "dd64114721edca5808872190e7e2e927ee2e994c"

SRC_URI = "git://git.kernel.org/pub/scm/linux/kernel/git/dhowells/keyutils.git;protocol=git \
          file://keyutils_fix_library_install.patch \
          "
SRC_URI_append_arm = " file://keyutils-arm-remove-m32-m64.patch"
SRC_URI_append_x86 = " file://keyutils_fix_x86_cflags.patch"
SRC_URI_append_x86-64 = " file://keyutils_fix_x86-64_cflags.patch"

S = "${WORKDIR}/git"

INSTALL_FLAGS = " \
BINDIR=${bindir} \
SBINDIR=${sbindir} \
INCLUDEDIR=${includedir} \
ETCDIR=${sysconfdir} \
LIBDIR=${libdir} \
USRLIBDIR=${libdir} \
SHAREDIR=${datadir} \
MAN1=${mandir}/man1 \
MAN3=${mandir}/man3 \
MAN5=${mandir}/man5 \
MAN8=${mandir}/man8 \
DESTDIR=${D}"

do_install() {
    cd ${S} && oe_runmake ${INSTALL_FLAGS} install

    # Debugging script of unknown value, not packaged.
    rm -f "${D}${datadir}/request-key-debug.sh"
}

BBCLASSEXTEND = "native"
