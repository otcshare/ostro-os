DESCRIPTION = "A Sample Node App"
HOMEPAGE = "http://127.0.0.1"
LICENSE = "MIT"

LIC_FILES_CHKSUM = "file://COPYING.MIT;md5=838c366f69b72c5df05c96dff79b35f2"

DEPENDS = "nodejs-native"
RDEPENDS_${PN} += "nodejs"

SRC_URI = "file://sample.js \
           file://package.json \
           file://COPYING.MIT \
           file://manifest.in \
"

OSTRO_USER_NAME = "test"
OSTRO_APP_NAME  = "node0"

# use ostro-app support class
inherit ostro-app

S = "${WORKDIR}/"

# we don't care about debug for the few binary node modules
INHIBIT_PACKAGE_DEBUG_SPLIT = "1"
INSANE_SKIP_${PN} = "staticdev"

# Manually install this simple app.
do_install () {
    install -d ${D}${OSTRO_APP_ROOT}/lib/node_modules/${OSTRO_APP_NAME}
    install -m 0644 sample.js package.json COPYING.MIT \
        ${D}${OSTRO_APP_ROOT}/lib/node_modules/${OSTRO_APP_NAME}/
    install -m 0644 manifest.in ${D}${OSTRO_APP_ROOT}/manifest.in
}
