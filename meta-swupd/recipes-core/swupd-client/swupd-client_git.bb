SUMMARY = "swupd sofware update from Clear Linux - client component"
HOMEPAGE = "https://github.com/clearlinux/swupd-client"
LICENSE = "GPL-2.0"
LIC_FILES_CHKSUM = "file://COPYING;md5=f8d90fb802930e30e49c39c8126a959e"

DEPENDS = "glib-2.0 curl openssl libarchive bsdiff"

PV = "3.6.0+git${SRCPV}"
SRC_URI = "\
    git://github.com/clearlinux/swupd-client.git;protocol=https \
    file://Change-systemctl-path-to-OE-systemctl-path.patch \
    file://0001-Add-configure-option-to-re-enable-updating-of-config.patch \
"
SRCREV = "f4000c5b22be47ec1af2f8748fd71a36148b5dc4"

S = "${WORKDIR}/git"

RDEPENDS_${PN}_append_class-target = " oe-swupd-helpers bsdtar"
# We check /etc/os-release for the current OS version number
RRECOMMENDS_${PN}_class-target = "os-release"

# TODO: we inherit autotools-brokensep because the Makefile calls a perl script
# in ${S} during one of its steps.
inherit pkgconfig autotools-brokensep systemd

EXTRA_OECONF = "\
    --with-systemdsystemunitdir=${systemd_system_unitdir} \
    --enable-bsdtar \
    --disable-tests \
"

PACKAGECONFIG ??= "stateless"
PACKAGECONFIG[stateless] = ",--disable-stateless"

SWUPD_VERSION_URL ??= "example.com"
SWUPD_CONTENT_URL ??= "example.com"
SWUPD_FORMAT ??= "3"
do_install_append () {
    # TODO: This should be a less os-specific directory and not hard-code datadir
    install -d ${D}$/usr/share/clear/bundles

    # Write default values to the configuration hierarchy (since 3.4.0)
    install -d ${D}/usr/share/defaults/swupd
    echo "{SWUPD_VERSION_URL}" >> ${D}/usr/share/defaults/swupd/versionurl
    echo "{SWUPD_CONTENT_URL}" >> ${D}/usr/share/defaults/swupd/contenturl
    echo "{SWUPD_FORMAT}" >> ${D}/usr/share/defaults/swupd/format
}

FILES_${PN} += "\
    /usr/share \
    ${systemd_system_unitdir}/multi-user.target.wants* \
    /var/lib/swupd \
"

SYSTEMD_SERVICE_${PN} = "check-update.timer check-update.service"
SYSTEMD_AUTO_ENABLE_${PN} = "disable"

BBCLASSEXTEND = "native"
