SUMMARY = "swupd sofware update from Clear Linux - client component"
LICENSE = "GPL-2.0"
LIC_FILES_CHKSUM = "file://COPYING;md5=04d0b48662817042d80393e7511fa41b \
                    file://bsdiff/LICENSE;md5=0dbe7a50f028269750631fcbded3846a"

SRC_URI = "\
    https://download.clearlinux.org/releases/5700/clear/source/SRPMS/${BPN}-${PV}-105.src.rpm;extract=${BP}.tar.gz \
    file://Fix-build-failure-on-Yocto.patch \
    file://Right-usage-of-AC_ARG_ENABLE-on-bzip2.patch \
    file://Change-systemctl-path-to-OE-systemctl-path.patch \
    file://0001-Tolerate-quotes-in-os-release-files.patch \
    file://0005-swupd-client-Add-existence-check-to-staging-target.patch \
    file://0006-Backport-Use-rename-instead-of-tar-transform.patch \
    file://0007-Add-compatibility-with-libarchive-s-bsdtar-command.patch \
    file://0001-log.c-avoid-segfault-and-show-staging-file-name.patch \
    file://0002-downloads-minimize-syscalls-to-improve-performance.patch \
    file://0001-Add-configure-option-to-re-enable-updating-of-config.patch \
"

SRC_URI[md5sum] = "5d272c62edb8a9c576005ac5e1182ea3"
SRC_URI[sha256sum] = "45df259a7dc2fed985ee9961e112120fc46670dd75476c3262fc6804b1c66fb8"

DEPENDS = "glib-2.0 curl openssl libarchive"
RDEPENDS_${PN}_append_class-target = " oe-swupd-helpers bsdtar"
# We check /etc/os-release for the current OS version number
RRECOMMENDS_${PN}_class-target = "os-release"

inherit pkgconfig autotools-brokensep systemd

EXTRA_OECONF = "--with-systemdsystemunitdir=${systemd_system_unitdir} --enable-bsdtar"

PACKAGECONFIG ??= "stateless"
PACKAGECONFIG[stateless] = ",--disable-stateless"

#TODO: create and install /var/lib/swupd/{delta,staged/download}
do_install_append () {
    # swupd-client 2.87 doesn't (succesfully) create these and fails to update
    # should they not exist. This is due to a bash-specific shell command
    # called to create the directories 'mkdir -p /var/lib/{delta,staged,download}'
    install -d ${D}/var/lib/swupd/delta
    install -d ${D}/var/lib/swupd/download
    install -d ${D}/var/lib/swupd/staged

    # TODO: This should be a less os-specific directory and not hard-code datadir
    install -d ${D}/usr/share/clear/bundles
}

FILES_${PN} += "\
    /usr/share/clear \
    ${systemd_system_unitdir}/multi-user.target.wants* \
    /var/lib/swupd \
"

SYSTEMD_SERVICE_${PN} = "check-update.timer check-update.service"
SYSTEMD_AUTO_ENABLE_${PN} = "disable"

BBCLASSEXTEND = "native"
