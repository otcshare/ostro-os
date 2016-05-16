require connman.inc

SRC_URI  = "${KERNELORG_MIRROR}/linux/network/${BPN}/${BP}.tar.xz \
            file://0001-plugin.h-Change-visibility-to-default-for-debug-symb.patch \
            file://0001-Detect-backtrace-API-availability-before-using-it.patch \
            file://0002-resolve-musl-does-not-implement-res_ninit.patch \
            file://0003-Fix-header-inclusions-for-musl.patch \
            file://0001-iptables-Add-missing-function-item-of-xtables-to-mat.patch \
            file://connman \
            file://connman.conf \
            file://connman.service \
            file://net.connman.conf \
            "
SRC_URI[md5sum] = "cb1c413fcc4f49430294bbd7a92f5f3c"
SRC_URI[sha256sum] = "88fcf0b6df334796b90e2fd2e434d6f5b36cd6f13b886a119b8c90276b72b8e2"

RRECOMMENDS_${PN} = "connman-conf"

do_install_append() {
    # Install updated systemd service file
    install -d ${D}${systemd_unitdir}/system
    install -m 0644 ${WORKDIR}/connman.service ${D}${systemd_unitdir}/system/

    # Install sysusers file
    install -d ${D}${libdir}/sysusers.d
    install -m 0644 ${WORKDIR}/connman.conf ${D}${libdir}/sysusers.d/

    # Install D-Bus policy file, change the name
    install -d ${D}${sysconfdir}/dbus-1/system.d
    install -m 0644 ${WORKDIR}/net.connman.conf ${D}${sysconfdir}/dbus-1/system.d/connman.conf
}

FILES_${PN} += "${libdir}/sysusers.d"
