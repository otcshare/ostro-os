SUMMARY = "IoT DevKit related components"
LICENSE = "MIT"

inherit packagegroup

RDEPENDS_${PN} = " \
    hid-api \
    linuxptp \
    mraa \
    tempered \
    upm \
    soletta-dev-app \
"
