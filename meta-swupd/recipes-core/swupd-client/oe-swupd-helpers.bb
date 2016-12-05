SUMMARY = "OE swupd helper files"
DESCRIPTION = "swupd-client assumes the presence of various helpers, this is a minimal OE \
implementation of the required scripts and systemd units. \
Scripts are modified versions of those in clr-specialized-updaters and units are modified \
versions of those in clr-systemd-config"
LICENSE = "GPL-2.0"
LIC_FILES_CHKSUM = "file://${COREBASE}/meta/files/common-licenses/GPL-2.0;md5=801f80980d171dd6425610833a22dbe6"

SRC_URI = "file://update-triggers.target \
           file://catalog-trigger.service \
           file://ldconfig-trigger.service \
           file://tmpfiles-trigger.service \
           file://clr_pre_update.sh \
           file://kernel_updater.sh \
           file://systemdboot_updater.sh \
           "

inherit allarch distro_features_check systemd

REQUIRED_DISTRO_FEATURES = "systemd"

do_install () {
    install -d ${D}${systemd_system_unitdir}
    for svc in `find ${WORKDIR} -maxdepth 1 -name *.target -o -name *.service`; do
        install -m 0644 $svc ${D}${systemd_system_unitdir}/
        sed -i -e s#/bin#${base_bindir}# ${D}${systemd_system_unitdir}/`basename $svc`
        sed -i -e s#/sbin#${base_sbindir}# ${D}${systemd_system_unitdir}/`basename $svc`
        sed -i -e s#/lib#${base_libdir}# ${D}${systemd_system_unitdir}/`basename $svc`
    done

    # NOTE: swupd-client hard-codes /usr/bin
    install -d ${D}/usr/bin
    for helper in `find ${WORKDIR} -maxdepth 1 -name *.sh`; do
        install $helper ${D}/usr/bin/
    done
}

FILES_${PN} += "${systemd_system_unitdir}"
