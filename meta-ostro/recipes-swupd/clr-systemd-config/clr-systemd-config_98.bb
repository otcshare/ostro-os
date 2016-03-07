LICENSE = "LGPLv2.1"
LIC_FILES_CHKSUM = "file://LICENSE;md5=4fbd65380cdd255951079008b364516c"

SUMMARY = "Clear systemd config files for swupd"

SRC_URI = " \
  file://clr-systemd-config-${PV}.tar.gz \
  file://0001-change-clear-path-to-Ostro-path.patch \
  file://0002-systemd-service-for-updating-the-efi-combo.patch \
"

SRC_URI[md5sum] = "bc2fa9e8728c774d779edc094c9018d2"
SRC_URI[sha256sum] = "f6c1bc9f815ad002b82d2702fc79dd28ead2361533479207efef65173e1f5503"

REQUIRED_DISTRO_FEATURES = "systemd"

DEPENDS += "swupd-client systemd"

inherit pkgconfig systemd autotools distro_features_check

do_install_append () {
  rm ${D}${libdir}/modules-load.d/bridge-netfilter.conf
  rm ${D}${libdir}/sysusers.d/clear.conf
  rm ${D}${systemd_unitdir}/clr-image-triggers
  rm ${D}${systemd_unitdir}/system-preset/80-clear.preset
  rm ${D}${systemd_unitdir}/network/80-virtual.network
  rm ${D}${systemd_unitdir}/network/80-wlan.network
  rm ${D}${systemd_unitdir}/network/80-dhcp.network
  rm ${D}${systemd_unitdir}/journald.conf.d/clear.conf
  rm ${D}${systemd_unitdir}/bootchart.conf.d/clear.conf
  rm ${D}${systemd_unitdir}/system/firstboot-triggers.service
  rm ${D}${systemd_unitdir}/system/multi-user.target.wants/firstboot-triggers.service
  rm ${D}${systemd_unitdir}/system/opt-rootfs-proc.mount
  rm ${D}${systemd_unitdir}/system/opt-rootfs.mount
  rm ${D}${systemd_unitdir}/system/container-workload.service
  rm ${D}${systemd_unitdir}/system/container.target
  rm ${D}${datadir}/defaults/etc/passwd
  rm ${D}${datadir}/defaults/etc/shadow
  rm ${D}${datadir}/defaults/etc/group
  rm ${D}${datadir}/defaults/etc/gshadow
  rm ${D}/${base_prefix}/lib/udev/rules.d/80-kvm.rules

  rmdir ${D}${libdir}/sysusers.d
  rmdir ${D}${libdir}/modules-load.d
  rmdir ${D}${systemd_unitdir}/system-preset
  rmdir ${D}${systemd_unitdir}/network
  rmdir ${D}${systemd_unitdir}/journald.conf.d
  rmdir ${D}${systemd_unitdir}/bootchart.conf.d
  rmdir ${D}${datadir}/defaults/etc
  rmdir ${D}${datadir}/defaults
  rmdir ${D}${datadir}
  rmdir ${D}${libdir}
  rmdir ${D}/usr
  rmdir ${D}/${base_prefix}/lib/udev/rules.d
  rmdir ${D}/${base_prefix}/lib/udev


  cp  --preserve=mode,timestamp ${S}/system/efi-combo-trigger.service ${D}${systemd_unitdir}/system/
}

FILES_${PN} += " \
  ${systemd_unitdir}/system/ \
"
