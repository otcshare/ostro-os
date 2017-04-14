SUMMARY = "Applications and Scripts for libyami."
DESCRIPTION = "Applications and Scripts for libyami."

HOMEPAGE = "https://github.com/01org/libyami-utils"
BUGTRACKER = "https://github.com/01org/libyami-utils/issues/new"

LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=e3fc50a88d0a364313df4b21ef20c29e"

SRC_URI = "https://github.com/01org/libyami-utils/archive/${PV}.tar.gz"

SRC_URI[md5sum] = "7473e643e09296c20ed1286743906004"
SRC_URI[sha256sum] = "66865408b63d09a80f1305828898c9cb5e7d57585b944b08148c92d774ba8dcd"

S = "${WORKDIR}/libyami-utils-${PV}"

DEPENDS = "libva libyami"

EXTRA_OECONF = " --enable-tests-gles --disable-md5"

inherit autotools pkgconfig distro_features_check

REQUIRED_DISTRO_FEATURES = "opengl"
