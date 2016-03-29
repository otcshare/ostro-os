DESCRIPTION = "Revised mininal application 'framework'."
HOMEPAGE = "http://github.com/01org/iot-app-fw"
LICENSE = "BSD-3-Clause"

LIC_FILES_CHKSUM = "file://LICENSE-BSD;md5=f9f435c1bd3a753365e799edf375fc42"

DEPENDS = "json-c systemd"

SRC_URI = " \
    git://git@github.com/ostroproject/iot-app-fw.git;protocol=https;branch=kli/devel/smpl \
    file://80-container-host0.network \
    file://80-container-ve.network \
  "

SRCREV = "d6646e157becbfc8deeea16350b2809ef652dfad"

inherit autotools pkgconfig systemd

AUTO_LIBNAME_PKGS = ""

S = "${WORKDIR}/git"

# possible package configurations
PACKAGECONFIG ??= ""

FILES_${PN} = "${base_libdir}/systemd/system-generators/iot-service-generator \
               ${libexecdir}/iot-app-fw \
               ${libdir}/systemd/network/80-container-host0.network \
               ${libdir}/systemd/network/80-container-ve.network \
"

FILES_${PN}-dbg =+ "${base_libdir}/systemd/system-generators/.debug"

do_install_append () {
    mkdir -p ${D}${libdir}/systemd/network
    cp ../80-container-host0.network ${D}${libdir}/systemd/network
    cp ../80-container-ve.network ${D}${libdir}/systemd/network
}
