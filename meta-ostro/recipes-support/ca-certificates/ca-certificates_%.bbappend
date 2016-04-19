FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI_append = "\
    file://update-ca-certificates-support-Toybox.patch \
"
