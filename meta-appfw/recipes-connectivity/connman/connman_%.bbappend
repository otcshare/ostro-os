FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

SRC_URI += " \
    file://0001-nat-don-t-assume-IP-forwarding-is-initially-off.patch \
    file://0001-main-add-ve-and-vb-to-the-default-interface-blacklis.patch \
"
