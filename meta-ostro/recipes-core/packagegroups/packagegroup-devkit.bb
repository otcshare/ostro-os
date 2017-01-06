SUMMARY = "IoT DevKit related components"
LICENSE = "MIT"

inherit packagegroup

RDEPENDS_${PN} = " \
    linuxptp \
    mraa \
    mraa-utils \
    upm \
    soletta-dev-app \
"
