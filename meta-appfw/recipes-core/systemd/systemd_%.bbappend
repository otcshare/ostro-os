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
