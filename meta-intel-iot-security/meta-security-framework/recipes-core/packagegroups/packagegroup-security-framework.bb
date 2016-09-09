SUMMARY = "Security middleware components"
LICENSE = "MIT"

inherit packagegroup

RDEPENDS_${PN}_append_smack = " \
    smacknet \
"
