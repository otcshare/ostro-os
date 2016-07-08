SUMMARY = "Intel Galileo & Intel Edison IO Plugin for Johnny-Five JavaScript Robotics"
HOMEPAGE = "https://github.com/rwaldron/galileo-io"
SRC_URI = "npm://registry.npmjs.org;name=galileo-io;version=${PV} \
           file://npm-shrinkwrap.json;subdir=npmpkg \
           file://lockdown.json;subdir=npmpkg"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE-MIT;md5=ff2fe567e4b5d1db887b73bcbb798fd4 \
                    file://node_modules/remapped/LICENSE;md5=976108e041d95aec03ec5c4246bad937 \
                    file://node_modules/remapped/node_modules/traverse/LICENSE;md5=0f6546e91538ce8c26b2da1623705c62 \
                    file://node_modules/remapped/node_modules/getobject/LICENSE-MIT;md5=159111132f87941857a4f42d60c880c8 \
                    file://node_modules/es6-promise/LICENSE;md5=6e73e44544d76c1978a076a8292d031a \
                    file://node_modules/es6-shim/LICENSE;md5=508a108665f3b7140d113af9c579ba24"

RDEPENDS_${PN} += "johnny-five node-mraa"
S = "${WORKDIR}/npmpkg"

NPM_SHRINKWRAP := "${THISDIR}/${PN}/npm-shrinkwrap.json"
NPM_LOCKDOWN := "${THISDIR}/${PN}/lockdown.json"

inherit npm

LICENSE_${PN}-es6-promise = "MIT"
LICENSE_${PN}-es6-shim = "MIT"
LICENSE_${PN}-remapped-getobject = "MIT"
LICENSE_${PN}-remapped-traverse = "MIT"
LICENSE_${PN}-remapped = "MIT"
LICENSE_${PN} = "MIT"
