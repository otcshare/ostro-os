FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

# We want/need systemd-networkd
PACKAGECONFIG_append = " iptc networkd"

# Patch systemd-nspawn to
#   - delay binary/OS-tree check after mounts
#   - support starting DHCP client in non-system containers
SYSTEMD_APPFW_PATCHES_228 = " \
    file://228/0001-nspawn-don-t-check-binary-OS-tree-before-all-mounts-.patch \
    file://228/0002-nspawn-added-support-for-starting-DHCP-client-in-non.patch \
"

SYSTEMD_APPFW_PATCHES_229 = " \
    file://229/0001-nspawn-don-t-check-binary-OS-tree-before-all-mounts-.patch \
    file://229/0002-nspawn-added-support-for-starting-DHCP-client-in-non.patch \
"

SRC_URI += " ${@d.getVar('SYSTEMD_APPFW_PATCHES_' + d.getVar('PV', False)[0:3], True) or ''}"

# systemd-nspawn needs getent (from glibc).
RDEPENDS_${PN} += "glibc-getent"

# Separate systemd-networkd to a subpackage.
PACKAGES_prepend     = "${PN}-networkd "
FILES_${PN}-networkd = " \
    ${base_libdir}/systemd/systemd-networkd \
    ${base_libdir}/systemd/system/systemd-network.service \
    ${base_libdir}/systemd/system/systemd-network.socket \
"

# And override service activation for the new subpackage.
SYSTEMD_PACKAGES += "${PN}-networkd"
SYSTEMD_SERVICE_${PN}-networkd = "systemd-networkd.socket"

RDEPENDS_${PN} += "systemd-networkd"
