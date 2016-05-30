# Copyright (C) 2016 Intel Corporation.
# Released under the MIT license (see COPYING.MIT for the terms)

DESCRIPTION = "Groupcheck -- a minimal polkit replacement"
HOMEPAGE = "http://github.com/ostroproject/groupcheck"
LICENSE = "LGPL2.1"
LIC_FILES_CHKSUM = "file://COPYING;md5=4fbd65380cdd255951079008b364516c"

SRC_URI = "git://github.com/ostroproject/groupcheck.git;protocol=git;rev=662f08b205f8d1783edbe07faa4d49fe5e795523"
SRCREV = "662f08b205f8d1783edbe07faa4d49fe5e795523"

DEPENDS = "systemd"

S = "${WORKDIR}/git"

inherit autotools systemd pkgconfig

# Depend on a policy ruleset. If no ruleset is specified then use the
# default configuration.
VIRTUAL-RUNTIME_groupcheck-settings ?= "groupcheck-settings-default"
RDEPENDS_${PN} += "${VIRTUAL-RUNTIME_groupcheck-settings}"

do_install_append() {
    install -d ${D}${systemd_unitdir}/system
    install -d ${D}${sysconfdir}/dbus-1/system.d
    install -d ${D}${libdir}/sysusers.d

    install -m 0644 ${S}/groupcheck.service ${D}${systemd_unitdir}/system/
    install -m 0644 ${S}/org.freedesktop.PolicyKit1.conf ${D}${sysconfdir}/dbus-1/system.d/
    install -m 0644 ${S}/groupcheck.conf ${D}${libdir}/sysusers.d/
}

FILES_${PN} += "${libdir}/sysusers.d/groupcheck.conf"

SYSTEMD_SERVICE_${PN} = "groupcheck.service"
