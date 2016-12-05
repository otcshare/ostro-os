SUMMARY = "swupd sofware update from Clear Linux - server component"
HOMEPAGE = "https://github.com/clearlinux/swupd-server"
LICENSE = "GPL-2.0"
LIC_FILES_CHKSUM = "file://COPYING;md5=f8d90fb802930e30e49c39c8126a959e"

DEPENDS = "file glib-2.0 rsync openssl libarchive bsdiff bzip2"
# Need the special "-replacement" variant because bzip2 and file
# are assumed to be provided and would not get built.
DEPENDS_append_class-native = " file-replacement-native bzip2-replacement-native"

# This matches the SWUPD_TOOLS_FORMAT in swupd-image.bbclass.
# When updating to a new release which changes the format of
# the output, copy the recipe first to ensure that the old
# release is still available if needed by swupd-image.bbclass,
# then bump this number.
#
# The rest of the recipe ensures that different swupd-server
# versions can be build and installed in parallel (format
# number embedded in PN and the resulting files).
SWUPD_SERVER_FORMAT = "3"
PN = "swupd-server-format${SWUPD_SERVER_FORMAT}"
FILESEXTRAPATHS_prepend = "${THISDIR}/swupd-server-3.2.5:"
PV = "3.2.5+git${SRCPV}"
SRC_URI = "git://github.com/clearlinux/swupd-server.git;protocol=https \
           file://0025-swupd_make_pack-fix-extracting-files-with-bsdtar.patch \
           file://0026-fullfiles.c-fix-invalid-LOG-call.patch \
           file://0027-update-control-over-parallelism.patch \
           file://0028-enable-locales-in-all-programs.patch \
           file://0029-fullfiles-use-libarchive-directly.patch \
           file://0001-swupd-create-update-alternative-input-layout.patch \
           file://0002-add-logging-to-stdout.patch \
           file://swupd_create_fullfiles-avoid-segfault-when-nothing-c.patch \
           file://0001-delta.c-fix-xattr-test-after-patching.patch \
           file://0002-pack.c-do-not-clean-packstage.patch \
           file://0003-swupd_create_pack-download-original-files-on-demand-.patch \
           file://0001-create_pack-rely-less-on-previous-builds.patch \
           file://0002-create_pack-download-fullfile-on-demand-for-packs.patch \
           file://0003-create_pack-abort-delta-handling-early-when-impossib.patch \
           file://0001-type_change.c-allow-transition-dir-symlink.patch \
           "
SRCREV = "ddca171dad32229ceeff8b8527a179610b88ce55"

S = "${WORKDIR}/git"

inherit pkgconfig autotools

EXTRA_OECONF = "--enable-bzip2 --enable-lzma --disable-stateless --disable-tests --enable-bsdtar"

# safer-calls-to-system-utilities.patch uses for loop initial declaration
CFLAGS_append = " -std=c99"

RDEPENDS_${PN} = "rsync"
RDEPENDS_${PN}_class-target = " bsdtar"

BBCLASSEXTEND = "native"

do_install_append () {
    for i in ${D}${bindir}/swupd_*; do
        mv $i ${i}_${SWUPD_SERVER_FORMAT}
    done
}
