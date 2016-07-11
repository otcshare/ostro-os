LICENSE="GPLv2"
LIC_FILES_CHKSUM="file://COPYING;md5=e197d5641bb35b29d46ca8c4bf7f2660"

inherit native

BPN="VirtualBox"

DEPENDS=" \
    libxml2-native glib-2.0-native libidl-native acpica-native cdrtools-native \
    libpng-native zlib-native openssl-native curl-native libcap-native \
    makeself-native libpam-native libxslt-native \
"

SRC_URI=" \
    http://download.virtualbox.org/virtualbox/${PV}/VirtualBox-${PV}.tar.bz2 \
    file://configure.patch \
    file://xpidl-build-fixes.patch \
    file://include-dir.patch \
    file://remove-x11.patch \
    file://fix-linker-flags.patch \
    file://disable-guest-additions.patch \
"

SRC_URI[md5sum] = "2701f423f2828cab4405098982f4f446"
SRC_URI[sha256sum] = "9134b04ca21ca23534e2300aab5ab7ff60d21b56bfd2e21504316bfee73afa87"

# export path to native libdir, as this is needed during build
# (see xpidl build fix patch)
export VIRTUALBOX_YOCTO_LIBDIR="${STAGING_LIBDIR_NATIVE}"

# The build files seem to override LDFLAGS, so re-export it with different name and patch files to use it
export VIRTUALBOX_YOCTO_LDFLAGS="${LDFLAGS}"

# Disable everything we do not need (which turns out to be almost everything)
VBOX_CONF = " \
    --disable-hardening \
    --disable-python \
    --disable-java \
    --disable-vmmraw \
    --disable-sdl-ttf \
    --disable-alsa \
    --disable-pulse \
    --disable-dbus \
    --disable-kmods \
    --disable-opengl \
    --disable-extpack \
    --disable-docs \
    --disable-libvpx \
    --disable-udptunnel \
    --disable-devmapper \
    --disable-vmmraw \
    --build-headless \
    --with-makeself='${STAGING_BINDIR_NATIVE}/makeself.sh' \
    "

# As we do not use either autotools or cmake, we have to call configure manually
do_configure() {
    ./configure ${VBOX_CONF}
}

do_compile() {
    . ./env.sh
    kmk
}

do_install() {
    # minimal set of files for VBoxManage
    ARCH_DIR=`ls ${B}/out`

    install -d ${D}${libdir}/vboxmanage
    install -m 0755 ${B}/out/${ARCH_DIR}/release/bin/VBoxManage ${D}${libdir}/vboxmanage
    install -m 0644 ${B}/out/${ARCH_DIR}/release/bin/VBoxDDU.so ${D}${libdir}/vboxmanage
    install -m 0644 ${B}/out/${ARCH_DIR}/release/bin/VBoxRT.so ${D}${libdir}/vboxmanage
    install -m 0644 ${B}/out/${ARCH_DIR}/release/bin/VBoxXPCOM.so ${D}${libdir}/vboxmanage
    install -m 0755 ${B}/out/${ARCH_DIR}/release/bin/VBoxSVC ${D}${libdir}/vboxmanage
    install -m 0755 ${B}/out/${ARCH_DIR}/release/bin/VBoxXPCOMIPCD ${D}${libdir}/vboxmanage

    install -d ${D}${libdir}/vboxmanage/components
    install -m 0644 ${B}/out/${ARCH_DIR}/release/bin/components/VBoxC.so ${D}${libdir}/vboxmanage/components
    install -m 0644 ${B}/out/${ARCH_DIR}/release/bin/components/VBoxSVCM.so ${D}${libdir}/vboxmanage/components
    install -m 0644 ${B}/out/${ARCH_DIR}/release/bin/components/VBoxXPCOMBase.xpt ${D}${libdir}/vboxmanage/components
    install -m 0644 ${B}/out/${ARCH_DIR}/release/bin/components/VBoxXPCOMIPCC.so ${D}${libdir}/vboxmanage/components
    install -m 0644 ${B}/out/${ARCH_DIR}/release/bin/components/VirtualBox_XPCOM.xpt ${D}${libdir}/vboxmanage/components


    install -d ${D}${bindir}
    ln -sf ../lib/vboxmanage/VBoxManage ${D}${bindir}/VBoxManage
}
