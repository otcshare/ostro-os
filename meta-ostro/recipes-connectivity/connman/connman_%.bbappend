FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI_append = "\
    file://0001-iptables-added-support-for-iptables-locking.patch \
"
