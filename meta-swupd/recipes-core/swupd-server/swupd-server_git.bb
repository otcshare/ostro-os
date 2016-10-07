SUMMARY = "swupd sofware update from Clear Linux - server component"
HOMEPAGE = "https://github.com/clearlinux/swupd-server"
LICENSE = "GPL-2.0"
LIC_FILES_CHKSUM = "file://COPYING;md5=f8d90fb802930e30e49c39c8126a959e"

DEPENDS = "file glib-2.0 rsync openssl libarchive bsdiff bzip2"
DEPENDS_append_class-native = " bzip2-replacement-native"

PV = "3.2.7+git${SRCPV}"
SRC_URI = "git://github.com/clearlinux/swupd-server.git;protocol=https \
           file://0025-swupd_make_pack-fix-extracting-files-with-bsdtar.patch \
           file://0026-fullfiles.c-fix-invalid-LOG-call.patch \
           file://0027-update-control-over-parallelism.patch \
           file://0028-enable-locales-in-all-programs.patch \
           file://0029-fullfiles-use-libarchive-directly.patch \
           file://0003-unified-dir-file-archiving.patch \
           file://0001-swupd-create-update-alternative-input-layout.patch \
           file://0002-add-logging-to-stdout.patch \
           "
SRCREV = "c4f61cb0239c77f2fcc008e3b4fc7a279a7c3a57"

S = "${WORKDIR}/git"

inherit pkgconfig autotools

EXTRA_OECONF = "--enable-bzip2 --enable-lzma --disable-stateless --disable-tests --enable-bsdtar"

# safer-calls-to-system-utilities.patch uses for loop initial declaration
CFLAGS_append = " -std=c99"

RDEPENDS_${PN} = "rsync"
RDEPENDS_${PN}_class-target = " bsdtar"

BBCLASSEXTEND = "native"
