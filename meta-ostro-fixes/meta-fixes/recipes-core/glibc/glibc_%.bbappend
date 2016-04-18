PACKAGES_prepend         = "${PN}-getent "
FILES_${PN}-getent       = "${bindir}/getent"
SUMMARY_${PN}-getent     = "Print entries from Name Service Switch libraries"
DESCRIPTION_${PN}-getent = "Prints entries from Name Service Switch libraries."

RDEPENDS_${PN}-utils    += "${PN}-getent"
