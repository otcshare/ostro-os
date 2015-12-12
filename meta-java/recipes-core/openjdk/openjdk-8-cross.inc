JDK_HOME = "${libdir_jvm}/openjdk-8"
JRE_HOME = "${libdir_jvm}/openjre-8"

DEPENDS = "\
    openjdk-8-native zip-native ant-native libxslt \
    jpeg libpng krb5 libffi fontconfig freetype \
"

PACKAGECONFIG ??= ""
PACKAGECONFIG[x11] = "--with-x,,libx11 xproto libxt libxext libxrender"
PACKAGECONFIG[cups] = "--with-cups,,cups"
PACKAGECONFIG[alsa] = "--with-alsa,,alsa-lib-native"

PACKAGECONFIG[jce] = "--enable-unlimited-crypto,,"

PACKAGECONFIG[zip] = "--with-zlib=system,--with-zlib=bundled,zlib,"
PACKAGECONFIG[gif] = "--with-giflib=system,--with-giflib=bundled,giflib,"

export WANT_LLVM_RELEASE = "3.5.2"
PACKAGECONFIG[zero] = "--with-jvm-variants=zero,,,"
PACKAGECONFIG[shark] = "--with-jvm-variants=zeroshark,,llvm3.5,"

require openjdk-8-common.inc

JAVA_HOME[unexport] = "1"

SRC_URI_append = "\
    file://jvm.cfg \
"

# do not use --wth-extra-cflags, it breaks building demos for jdk
# maybe disabling demos is more reasonable than avoiding --wth-extra-cflags
# needs discussion
EXTRA_OECONF_append = "\
    --with-jobs=${@get_jdk8_native_jobs(d)} \
    \
    --with-sys-root=${STAGING_DIR} \
    --with-tools-dir=${STAGING_DIR_NATIVE} \
    --with-boot-jdk=${STAGING_LIBDIR_NATIVE}/jvm/openjdk-8-native \
    --with-cacerts-file=${STAGING_LIBDIR_NATIVE}/jvm/openjdk-8-native/jre/lib/security/cacerts \
    \
    --disable-precompiled-headers \
    --disable-zip-debug-info \
    \
    ${@jdk_configure_options(d)} \
"

do_configure_append() {
    sed -i -e 's,POST_STRIP_CMD:=.*,POST_STRIP_CMD:=,g' ${B}/spec.gmk
}

export MAKE_VERBOSE = "y"
export MFLAGS="${@jdk_make_options(d)} MAKE_VERBOSE=y QUIETLY= VERBOSE=-s LOG_LEVEL=trace STRIP_POLICY=no_strip"

BUILD_LD="${BUILD_CCLD}"

EXTRA_OEMAKE_append = '\
    OE_CFLAGS="${CFLAGS}" \
    OE_CPPFLAGS="${CPPFLAGS}" \
    OE_CXXFLAGS="${CXXFLAGS}" \
    OE_LDFLAGS="${LDFLAGS}" \
    ${@jdk_make_options(d)} \
    ALT_SDT_H="${STAGING_INCDIR}" \
    ALT_CUPS_HEADERS_PATH="${STAGING_INCDIR}" \
    ALT_FREETYPE_HEADERS_PATH="${STAGING_INCDIR}/freetype2" \
    ALT_FREETYPE_LIB_PATH="${STAGING_LIBDIR}" \
    STRIP_POLICY=no_strip \
    MAKE_VERBOSE=y VERBOSE=-s LOG_LEVEL=trace \
    QUIETLY= \
    images \
'
