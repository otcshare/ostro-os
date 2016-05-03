DESCRIPTION = "CacaoVM for use as OpenEmbedded's Java VM"
HOMEPAGE = "http://www.cacaojvm.org/"
LICENSE  = "GPL-2.0"
LIC_FILES_CHKSUM = "file://COPYING;md5=59530bdf33659b29e73d4adb9f9f6552"
SECTION  = "interpreters"

DEPENDS_class-native = "zlib-native libtool-native ecj-initial-native fastjar-native classpath-native bdwgc-native"
PROVIDES_class-native = "virtual/java-native"

DEPENDS = "zlib libtool classpath virtual/javac-native bdwgc"
RPROVIDES_${PN} = "java2-runtime"

SRC_URI = "http://www.complang.tuwien.ac.at/cacaojvm/download/cacao-${PV}/cacao-${PV}.tar.xz \
           file://system-boehm-gc.patch \
           file://cacao-1.6.1-do-not-rely-on-absolute-paths.patch \
"

SRC_URI[md5sum] = "2c18478404afd1cffdd15ad1e9d85a57"
SRC_URI[sha256sum] = "eecc8bd1b528a028f43d9d1d0c06b97855bbf1d40e03826d911ebbc0b6971e12"

inherit java autotools-brokensep update-alternatives pkgconfig distro_features_check

REQUIRED_DISTRO_FEATURES = "x11"
REQUIRED_DISTRO_FEATURES_class-native := ""

EXTRA_OECONF_class-native = "\
    --enable-debug \
    --with-vm-zip=${datadir}/cacao/vm.zip \
    --with-java-runtime-library-classes=${datadir}/classpath/glibj.zip \
    --with-java-runtime-library-libdir=${libdir_jni}:${libdir} \
    --with-jni_md_h=${includedir}/classpath \
    --with-jni_h=${includedir}/classpath \
    --disable-test-dependency-checks \
    --disable-libjvm  \
"

CACHED_CONFIGUREVARS_class-native += "ac_cv_prog_JAVAC=${STAGING_BINDIR_NATIVE}/ecj-initial"

EXTRA_OECONF = "\
    --with-vm-zip=${datadir}/cacao/vm.zip \
    --disable-libjvm \
    --with-build-java-runtime-library-classes=${STAGING_DATADIR}/classpath/glibj.zip \
    --with-jni_h=${STAGING_INCDIR}/classpath \
    --with-jni_md_h=${STAGING_INCDIR}/classpath \
    --with-java-runtime-library-classes=${datadir}/classpath/glibj.zip \
    --with-java-runtime-library-libdir=${libdir_jni}:${libdir} \
    --disable-test-dependency-checks \
"

do_configure_prepend () {
    # upgrade m4 macros in source tree
    libtoolize --force --copy --install
    rm  -f src/mm/boehm-gc/ltmain.sh
    mkdir -p src/mm/boehm-gc/m4
}

do_install_append_class-target() {
    rm ${D}/${bindir}/java
}

FILES_${PN} = "${bindir}/${PN} ${libdir}/cacao/lib*.so ${libdir}/lib*.so* ${datadir}/${PN}"
FILES_${PN}-dbg += "${bindir}/.debug ${libdir}/.debug/lib*.so*"
FILES_${PN}-doc += "${datadir}/gc"

BBCLASSEXTEND = "native"
