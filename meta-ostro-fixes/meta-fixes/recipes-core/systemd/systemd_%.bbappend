FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

#
# We rely on systemd-networkd for configuring the host side of
# network interfaces for nspawned containers. Pull it in.
PACKAGECONFIG_append = " iptc networkd"

#
# Patch systemd-nspawn to
#   - delay binary/OS-tree check after all mounts are done
#   - support starting a custom DHCP client in non-system containers
#   - retry firewall rule modification for EAGAIN with a backoff
SYSTEMD_APPFW_PATCHES_229 = " \
    file://229/0001-nspawn-don-t-check-binary-OS-tree-before-all-mounts-.patch \
    file://229/0001-nspawn-added-support-for-starting-DHCP-client-in-non.patch \
    file://229/0001-nspawn-backoff-and-retry-if-firewall-modification-fa.patch \
"

SRC_URI += " ${@d.getVar('SYSTEMD_APPFW_PATCHES_' + d.getVar('PV', False)[0:3], True) or ''}"

#
# systemd-nspawn has a hard dependency on getent from glibc. We have an
# accompanying glibc patch that splits getent out to a subpackage of its
# own. Pull that in.
# Pull it in.
RDEPENDS_${PN} += "glibc-getent"

#
# Make systemd-networkd socket activated. It's a bit of a Yoctoism
# how we accomplish this but I couldn't come up with an easier way:
#  - we split out systemd-networkd to a subpackage of its own
#  - we override the service file for that subpackage to the socket
#  - we make the base package RDEPEND on the subpackage to keep the
#    former dependency consequences intact
PACKAGES_prepend     = "${PN}-networkd "
FILES_${PN}-networkd = " \
    ${base_libdir}/systemd/systemd-networkd \
    ${base_libdir}/systemd/system/systemd-networkd.service \
    ${base_libdir}/systemd/system/systemd-networkd.socket \
"

SYSTEMD_PACKAGES += "${PN}-networkd"
SYSTEMD_SERVICE_${PN}-networkd = "systemd-networkd.socket"

RDEPENDS_${PN} += "systemd-networkd"
