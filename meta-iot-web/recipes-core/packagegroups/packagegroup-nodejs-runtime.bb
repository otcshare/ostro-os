SUMMARY = "Runtime for NodeJS Apps"
LICENSE = "MIT"

inherit packagegroup

RDEPENDS_${PN} = " \
    iotivity-node \
    iot-rest-api-server \
    nodejs \
"
