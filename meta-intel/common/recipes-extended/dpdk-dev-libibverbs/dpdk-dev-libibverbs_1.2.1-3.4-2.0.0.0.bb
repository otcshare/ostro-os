DESCRIPTION = "libibverbs library to support Mellanox config"
HOMEPAGE = "https://github.com/Mellanox/dpdk-dev-libibverbs"
LICENSE = "GPLv2"
LIC_FILES_CHKSUM =  "file://COPYING;md5=7c557f27dd795ba77cc419dddc656b51"

SRC_URI = "https://github.com/Mellanox/dpdk-dev-libibverbs/archive/libibverbs-${PV}.tar.gz;name=${PN}"

SRC_URI[dpdk-dev-libibverbs.md5sum] = "65234ee278eb437a7069326f37cd4d86"
SRC_URI[dpdk-dev-libibverbs.sha256sum] = "a6471515556cb8d10ad471bb7efb8cf760b248a28aceb57d4534d50d572f56cd"

COMPATIBLE_MACHINE = "intel-corei7-64"

S = "${WORKDIR}/${PN}-libibverbs-${PV}"
COMPATIBLE_HOST = '(i.86|x86_64).*-linux'
DEPENDS = "libnl"

inherit pkgconfig autotools
