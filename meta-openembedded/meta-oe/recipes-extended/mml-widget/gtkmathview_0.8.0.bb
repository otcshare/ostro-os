HOMEPAGE = "http://helm.cs.unibo.it/mml-widget/"
DEPENDS = "t1lib gtk+ popt libxslt libxml2"

LICENSE = "LGPLv3"
LIC_FILES_CHKSUM = "file://COPYING;md5=6a6a8e020838b23406c81b19c1d46df6"

PR = "r3"
SRCREV = "0bc2cfa0a47aed2c8a63abd989cb8da4dcceb2ec"
PV = "0.8.0+git${SRCPV}"

SRC_URI = "git://github.com/GNOME/gtkmathview.git \
           file://use_hostcxx.patch \
	   file://0001-include-cstdio-to-get-printf-definitions.patch \
          "

S = "${WORKDIR}/git"

inherit autotools pkgconfig

do_configure_prepend() {
    sed -i -e s:AM_BINRELOC::g ${S}/configure.ac
}

# http://errors.yoctoproject.org/Errors/Details/35122/
PNBLACKLIST[gtkmathview] ?= "BROKEN: ERROR: QA Issue: mathview-frontend-libxml2.pc, mathview-frontend-libxml2-reader.pc failed sanity test (tmpdir)"
