# Copyright (C) 2016 Intel.
# Released under the MIT license (see COPYING.MIT for the terms)

DESCRIPTION = "Default groupcheck policy settings."
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = " \
    file://default-groupcheck.policy \
"

inherit update-alternatives

# use update-alternatives for letting several rulesets to be installed
# to the same sysroot
ALTERNATIVE_${PN} += "groupcheck.policy"
ALTERNATIVE_LINK_NAME[groupcheck.policy] = "${datadir}/defaults/etc/groupcheck.policy"
ALTERNATIVE_TARGET[groupcheck.policy] = "${datadir}/defaults/etc/default-groupcheck.policy"

# update-alternatives does not add the generated files automatically to
# FILES_${PN}

FILES_${PN} += "${datadir}/defaults/etc/"

do_install() {
    install -d ${D}${datadir}/defaults/etc
    install -m 0644 ${WORKDIR}/default-groupcheck.policy ${D}${datadir}/defaults/etc/default-groupcheck.policy
}
