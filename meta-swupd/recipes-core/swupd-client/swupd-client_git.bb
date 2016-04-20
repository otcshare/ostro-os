SUMMARY = "swupd sofware update from Clear Linux - client component"
HOMEPAGE = "https://github.com/clearlinux/swupd-client"
LICENSE = "GPL-2.0"
LIC_FILES_CHKSUM = "file://COPYING;md5=f8d90fb802930e30e49c39c8126a959e"

DEPENDS = "glib-2.0 curl openssl libarchive bsdiff"

PV = "3.3.0+git${SRCPV}"
SRC_URI = "\
    git://github.com/clearlinux/swupd-client.git;protocol=https \
    file://Change-systemctl-path-to-OE-systemctl-path.patch \
    file://0001-staging.c-Protect-tar-command-against-special-charac.patch \
    file://0001-Add-configure-option-to-re-enable-updating-of-config.patch \
"
SRCREV = "e4b2a32448d9fd9ab494f861f1bb143468659c75"

S = "${WORKDIR}/git"

RDEPENDS_${PN}_append_class-target = " oe-swupd-helpers bsdtar"
# We check /etc/os-release for the current OS version number
RRECOMMENDS_${PN}_class-target = "os-release"

inherit pkgconfig autotools systemd

EXTRA_OECONF = "\
    --with-systemdsystemunitdir=${systemd_system_unitdir} \
    --enable-bsdtar \
"

PACKAGECONFIG ??= "stateless"
PACKAGECONFIG[stateless] = ",--disable-stateless"

do_install_append () {
    # TODO: This should be a less os-specific directory and not hard-code datadir
    install -d ${D}${datadir}/clear/bundles
}

FILES_${PN} += "\
    /usr/share \
    ${systemd_system_unitdir}/multi-user.target.wants* \
    /var/lib/swupd \
"

SYSTEMD_SERVICE_${PN} = "check-update.timer check-update.service"
SYSTEMD_AUTO_ENABLE_${PN} = "disable"

BBCLASSEXTEND = "native"
