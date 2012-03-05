DESCRIPTION = "JUnit is a testing framework for Java"
DEPENDS = "fastjar-native"
LICENSE = "CLOSED"

SRC_URI = "http://rxtx.qbang.org/pub/rxtx/rxtx-2.2pre2.zip \
           file://zsystem_init_exception.patch \
           file://kfreebsd_port.patch \
           file://ttyACM_port.patch \
           file://original_debian_changes.patch \
           file://kfreebsd_libpthread.patch \
           file://sys_io_h_check.patch \
           file://port_to_hurd.patch \
           file://multiple_property_dirs.patch \
           file://uninstall_target.patch"

SRC_URI[md5sum] = "7eedb18e3f33a427e2b0e9be8ce3f94c"
SRC_URI[sha256sum] = "3c30373e760f444def3650c76c5a00ae12fb1d860ec008750d084f4880495b03"

S = "${WORKDIR}/rxtx-2.2pre2"

INSANE_SKIP_${PN} += "dev-so"

inherit autotools java-library

JARFILENAME = "RXTXcomm.jar"
EXTRA_OEMAKE += "RXTX_PATH=${D}${libdir_jni} \
                 JHOME=${D}${datadir_java}/ext"

do_configure_prepend() {
    # Ugly but don't complain to me, but upstream ;-)
    sed -e 's,bin/javah,bin/gjavah,g' \
        -e 's,bin/jar,bin/fastjar,g' \
        -e 's,\$(TOP)/libtool,\$(TOP)/\${host_alias}-libtool,g' -i ${S}/configure.in
    rm ${S}/acinclude.m4 \
       ${S}/aclocal.m4 \
       ${S}/ltconfig \
       ${S}/ltmain.sh
}

do_install_prepend() {
    install -d ${D}${libdir_jni}
    install -d ${D}${datadir_java}/ext
}

FILES_${PN} += "${libdir_jni}"
FILES_${PN}-dbg += "${libdir_jni}/.debug"
