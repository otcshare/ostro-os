FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

inherit systemd

# Make swupd "stateful" by letting it update files in /etc.
PACKAGECONFIG_remove = "stateless"

SRC_URI_append = "file://0001-Disable-boot-file-heuristics.patch \
                  file://efi_combo_updater.c \
                  ${@ 'file://efi-combo-trigger.service' if ${OSTRO_USE_DSK_IMAGES} else ''} \
                 "

RDEPENDS_${PN}_class-target_append = "${@ ' gptfdisk' if ${OSTRO_USE_DSK_IMAGES} else '' }"
DEPENDS_${PN}_append = " xattr-native"

# Get rid of check-update entirely, otherwise we cannot enable
# auto-activation.
SYSTEMD_SERVICE_${PN}_remove = "check-update.timer check-update.service"

# Optionally add our efi-combo-trigger.
SYSTEMD_SERVICE_${PN} += "${@ 'efi-combo-trigger.service' if ${OSTRO_USE_DSK_IMAGES} else ''}"

# And activate it.
SYSTEMD_AUTO_ENABLE_${PN} = "enable"

do_compile_append() {
    if [ "${OSTRO_USE_DSK_IMAGES}" = "True" ]; then
        ${CC} ${LDFLAGS} ${WORKDIR}/efi_combo_updater.c  -Os -o ${B}/efi_combo_updater `pkg-config --cflags --libs glib-2.0`
    fi
}

do_install_append () {
    if [ "${OSTRO_USE_DSK_IMAGES}" = "True" ]; then
        install -d ${D}/usr/bin
        install ${B}/efi_combo_updater ${D}/usr/bin/
        install -d ${D}/${systemd_system_unitdir}
        install -m 0644 ${WORKDIR}/efi-combo-trigger.service ${D}/${systemd_system_unitdir}
    fi

    # Don't install and enable check-update.timer by default
    rm -f ${D}/${systemd_system_unitdir}/check-update.* ${D}/${systemd_system_unitdir}/multi-user.target.wants/check-update.*
}

pkg_postinst_${PN}_append () {
    # Setting a label explicitly on the directory prevents it
    # from inheriting other undesired attributes like security.SMACK64TRANSMUTE
    # from upper folders (see xattr-images.bbclass for details).
    if ${@bb.utils.contains('DISTRO_FEATURES', 'smack', 'true', 'false', d)}; then
       setfattr -n security.SMACK64 -v "_" $D/var/lib/swupd
    fi
}
