JDK_DIR = "openjdk-8-native"
DEPENDS = "\
    icedtea7-native ant-native \
    libxslt-native attr-native \
    giflib-native jpeg-native libpng-native \
    glib-2.0-native freetype-native fontconfig-native \
    zlib-native zip-native \
    unzip-native make-native \
    ca-certificates-native openssl-native \
"

PACKAGECONFIG ??= ""
PACKAGECONFIG[x11] = "--with-x,,libx11-native xproto-native libxt-native libxext-native libxrender-native"
PACKAGECONFIG[cups] = "--with-cups,,cups"
PACKAGECONFIG[alsa] = "--with-alsa,,alsa-lib-native"
PACKAGECONFIG[jce] = "--enable-unlimited-crypto,,"

# do not use --wth-extra-cflags, it breaks building demos for jdk
# maybe disabling demos is more reasonable than avoiding --wth-extra-cflags
# needs discussion
EXTRA_OECONF_append = "\
    --with-jobs=${@get_jdk8_native_jobs(d)} \
    \
    --with-sys-root=${STAGING_DIR_NATIVE} \
    --with-tools-dir=${STAGING_DIR_NATIVE} \
    --with-boot-jdk=${STAGING_LIBDIR_NATIVE}/jvm/icedtea7-native \
    ${@jdk_configure_options(d)} \
"
# --with-boot-jdk=${WORKDIR}/fake-jdk

inherit native

require openjdk-8-common.inc

CFLAGS_append = "${@jdk_cpp_options(d)}"
CPPFLAGS_append = "${@jdk_cpp_options(d)}"
CXXFLAGS_append = "${@jdk_cpp_options(d)}"

export MAKE_VERBOSE = "y"
export MFLAGS="${@jdk_make_options(d)} MAKE_VERBOSE=y QUIETLY= VERBOSE=-s LOG_LEVEL=trace"

EXTRA_OEMAKE_append = ' \
    OE_CFLAGS="${CFLAGS}" \
    OE_CPPFLAGS="${CPPFLAGS}" \
    OE_CXXFLAGS="${CXXFLAGS}" \
    OE_LDFLAGS="${LDFLAGS}" \
    ${@jdk_make_options(d)} \
    MAKE_VERBOSE=y VERBOSE=-s LOG_LEVEL=trace \
    QUIETLY= \
    images \
'

do_compile_append() {
    set -x
    mkdir -p ${B}/certs
    for pem in $(find ${STAGING_DATADIR}/ca-certificates -name "*.crt")
    do
        bp=`basename ${pem}`
        alias=`echo ${bp} | sed -e 's,\.[^.]*$,,'`
        md5a=`echo ${alias} | md5sum | awk '{print $1}'`
        der=`echo ${bp} | sed -e 's,crt$,der,'`
        openssl x509 -in "${pem}" -inform pem -out "${B}/certs/${md5a}.der" -outform der
        ${B}/images/j2sdk-image/bin/keytool -importcert -noprompt -storepass changeit \
            -keystore "${B}/images/j2sdk-image/jre/lib/security/cacerts" \
            -alias "${alias}" -file "${B}/certs/${md5a}.der"
    done
    set +x
}

do_install() {
    rm -rf ${STAGING_LIBDIR_NATIVE}/jvm/${JDK_DIR}
    mkdir -p ${STAGING_LIBDIR_NATIVE}/jvm/${JDK_DIR}
    cp -rp ${B}/images/j2sdk-image/* ${STAGING_LIBDIR_NATIVE}/jvm/${JDK_DIR}

# clean up the mess from bootstrap
    for tool in jar java javac keytool pack200 unpack200
    do
        rm -f ${STAGING_BINDIR_NATIVE}/$tool

        ln -sf "../lib/jvm/${JDK_DIR}/bin/$tool" ${STAGING_BINDIR_NATIVE}/$tool
    done
}
