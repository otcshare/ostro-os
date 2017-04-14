SUMMARY = "Yami is media infrastructure base on libva"
DESCRIPTION = "Yet Another Media Infrastructure \
light weight hardware codec library base on VA-API "

HOMEPAGE = "https://github.com/01org/libyami"
BUGTRACKER = "https://github.com/01org/libyami/issues/new"

LICENSE = "Apache-2.0"
SRC_URI = "https://github.com/01org/libyami/archive/libyami-${PV}.tar.gz"

LIC_FILES_CHKSUM = "file://COPYING.LIB;md5=3b83ef96387f14655fc854ddc3c6bd57"

SRC_URI[md5sum] = "4e949cca98be87855f68af987c1eba3f"
SRC_URI[sha256sum] = "08acb7857a1a85c1d3341862d6b523c0eb1603adee454469cda765b6bf04f614"

S = "${WORKDIR}/libyami-libyami-${PV}"

PACKAGECONFIG ??= "${@bb.utils.contains("DISTRO_FEATURES", "x11", "x11", "", d)}"
PACKAGECONFIG[x11] = "--enable-x11,--disable-x11,virtual/libx11 libxrandr libxrender"

DEPENDS = "libva"
inherit autotools pkgconfig distro_features_check

REQUIRED_DISTRO_FEATURES = "opengl"
