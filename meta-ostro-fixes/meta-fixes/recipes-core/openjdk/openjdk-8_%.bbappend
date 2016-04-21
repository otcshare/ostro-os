FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

PATCHES_URI_append = " \
        file://openjdk8-silence-d_fortify_source-warning.patch;apply=no \
"
