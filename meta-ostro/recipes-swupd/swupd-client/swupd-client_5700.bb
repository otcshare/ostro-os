SUMMARY = "Software update client tool"
DESCRIPTION = "The swupd-client package provides a reference implementation of a software update client which performs file level updates of an OS, preferentially using binary deltas whenever possible for efficiency under an assumption that the OS develops with a release process aimed at rapidly deploying small incremental changes."
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=04d0b48662817042d80393e7511fa41b \
                    file://bsdiff/LICENSE;md5=0dbe7a50f028269750631fcbded3846a"

SRC_URI = " \
  file://swupd-client-${PV}.tar.gz \
  file://0001-change-systemctl-path-to-Ostro-systemctl-path.patch \
  file://0002-Fix-build-failure-on-Yocto.patch \
  file://0003-Right-usage-of-AC_ARG_ENABLE-on-bzip2.patch \
  file://0004-Tolerate-quotes-in-os-release-files.patch \
  file://efi_combo_updater.c \
  "
SRC_URI[md5sum] = "58671adf559dd18620f11caf4ccf83dd"
SRC_URI[sha256sum] = "09a70a423d10a6bf71f8675b7430c29a56f41f93493331c9ae515011713c229b"

inherit pkgconfig

DEPENDS = "zlib curl openssl xz glib-2.0"
RDEPENDS_${PN} = "xz tar gptfdisk glib-2.0 bash"

PACKAGECONFIG ??= "bzip2"
PACKAGECONFIG[bzip2] = "--enable-bzip2,--disable-bzip2,bzip2"

inherit pkgconfig autotools

EXTRA_OECONF = "--with-systemdsystemunitdir=${base_libdir}/systemd/system"

FILES_${PN} += " \
  ${datadir}/clear/update-ca/ \
  ${base_libdir}/systemd/system/ \
"

do_compile() {
  autotools_do_configure
  ${CC} ${LDFLAGS} ${WORKDIR}/efi_combo_updater.c  -Os -o ${B}/efi_combo_updater `pkg-config --cflags --libs glib-2.0`
}

do_install_append() {
  mkdir -p ${D}/usr/bin/
  cp ${B}/efi_combo_updater ${D}/usr/bin/
}
