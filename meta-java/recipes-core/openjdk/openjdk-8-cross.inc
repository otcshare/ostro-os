JDKPN = "openjdk-8"
JREPN = "openjre-8"

JDK_HOME = "${libdir_jvm}/${JDKPN}"
JRE_HOME = "${libdir_jvm}/${JREPN}"

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

FILES_${JREPN}_append = "\
    ${JRE_HOME}/bin/[a-z]* \
    ${JRE_HOME}/lib/[a-z]* \
    ${JRE_HOME}/LICENSE \
    ${JRE_HOME}/release \
"

FILES_${JDKPN}_append = "\
    ${JDK_HOME}/bin/[a-z]* \
    ${JDK_HOME}/lib/[a-z]* \
    ${JDK_HOME}/jre/bin/[a-z]* \
    ${JDK_HOME}/jre/lib/[a-z]* \
    ${JDK_HOME}/LICENSE \
    ${JDK_HOME}/jre/LICENSE \
    ${JDK_HOME}/release \
"

FILES_${JDKPN}-dev_append = "\
    ${JDK_HOME}/include \
"

FILES_${JDKPN}-dbg_append = "\
    ${JDK_HOME}/bin/.debug/ \
    ${JDK_HOME}/lib/.debug/ \
    ${JDK_HOME}/lib/${JDK_ARCH}/.debug/ \
    ${JDK_HOME}/lib/${JDK_ARCH}/jli/.debug/ \
    ${JDK_HOME}/jre/bin/.debug/ \
    ${JDK_HOME}/jre/lib/.debug/ \
    ${JDK_HOME}/jre/lib/${JDK_ARCH}/.debug/ \
    ${JDK_HOME}/jre/lib/${JDK_ARCH}/jli/.debug/ \
    ${JDK_HOME}/jre/lib/${JDK_ARCH}/native_threads/.debug/ \
    ${JDK_HOME}/jre/lib/${JDK_ARCH}/server/.debug/ \
    ${JDK_HOME}/jre/lib/${JDK_ARCH}/headless/.debug/ \
    ${JDK_HOME}/jre/lib/${JDK_ARCH}/xawt/.debug/ \
    ${JDK_HOME}/jre/lib/${JDK_ARCH}/client/.debug/ \
"

FILES_${JREPN}-dbg_append = "\
    ${JRE_HOME}/bin/.debug/ \
    ${JRE_HOME}/lib/.debug/ \
    ${JRE_HOME}/lib/${JDK_ARCH}/.debug/ \
    ${JRE_HOME}/lib/${JDK_ARCH}/jli/.debug/ \
    ${JRE_HOME}/lib/${JDK_ARCH}/server/.debug/ \
"

FILES_${JDKPN}-demo = " ${JDK_HOME}/demo ${JDK_HOME}/sample "
RDEPENDS_${JDKPN}-demo = " ${JDKPN} "

FILES_${JDKPN}-demo-dbg = "\
    ${JDK_HOME}/demo/jvmti/gctest/lib/.debug/ \
    ${JDK_HOME}/demo/jvmti/heapTracker/lib/.debug/ \
    ${JDK_HOME}/demo/jvmti/heapViewer/lib/.debug/ \
    ${JDK_HOME}/demo/jvmti/hprof/lib/.debug/ \
    ${JDK_HOME}/demo/jvmti/minst/lib/.debug/ \
    ${JDK_HOME}/demo/jvmti/mtrace/lib/.debug/ \
    ${JDK_HOME}/demo/jvmti/versionCheck/lib/.debug/ \
    ${JDK_HOME}/demo/jvmti/waiters/lib/.debug/ \
    ${JDK_HOME}/demo/jvmti/compiledMethodLoad/lib/.debug/ \
"

FILES_${JDKPN}-doc_append = "\
    ${JDK_HOME}/man \
    ${JDK_HOME}/ASSEMBLY_EXCEPTION \
    ${JDK_HOME}/THIRD_PARTY_README \
    ${JDK_HOME}/jre/ASSEMBLY_EXCEPTION \
    ${JDK_HOME}/jre/THIRD_PARTY_README \
"
FILES_${JREPN}-doc_append = "\
    ${JRE_HOME}/man \
    ${JRE_HOME}/ASSEMBLY_EXCEPTION \
    ${JRE_HOME}/THIRD_PARTY_README \
"

FILES_${JDKPN}-source = " ${JDK_HOME}/src.zip "

# Even though a vm is a hard dependency it is set as RRECOMMENDS so a single vm can get uninstalled:
# root@beaglebone:~/java# opkg remove openjdk-7-vm-shark
# No packages removed.
# Collected errors:
#  * print_dependents_warning: Package openjdk-7-vm-shark is depended upon by packages:
#  * print_dependents_warning:         openjdk-7-java
#  * print_dependents_warning: These might cease to work if package openjdk-7-vm-shark is removed.
#RRECOMMENDS_${JDKPN}-java = "java2-vm"

# There is a symlink to a .so but this one is valid.
INSANE_SKIP_${JDKPN}-common = "dev-so"

FILES_${JDKPN}-doc_append = "${JDK_HOME}/man"

do_compile_append() {
    find ${B}/images/j2sdk-image -name "*.jar" -print0 | \
      xargs -0 -n1 ${STAGING_LIBDIR_NATIVE}/jvm/openjdk-8-native/bin/pack200 --repack --effort=9 --segment-limit=-1 --modification-time=latest
    find ${B}/images/j2re-image -name "*.jar" -print0 | \
      xargs -0 -n1 ${STAGING_LIBDIR_NATIVE}/jvm/openjdk-8-native/bin/pack200 --repack --effort=9 --segment-limit=-1 --modification-time=latest --strip-debug
}

do_install_jdk() {
    rm -rf ${D}${JDK_HOME}
        mkdir -p ${D}${JDK_HOME}
    cp -rp ${B}/images/j2sdk-image/* ${D}${JDK_HOME}
    install -m644 ${WORKDIR}/jvm.cfg  ${D}${JDK_HOME}/jre/lib/${JDK_ARCH}/
    find ${D}${JDK_HOME} -name "*.debuginfo" -print0 | xargs -0 rm
}

do_install_jre() {
    rm -rf ${D}${JRE_HOME}
        mkdir -p ${D}${JRE_HOME}
    cp -rp ${B}/images/j2re-image/* ${D}${JRE_HOME}
    install -m644 ${WORKDIR}/jvm.cfg  ${D}${JRE_HOME}/lib/${JDK_ARCH}/
    find ${D}${JRE_HOME} -name "*.debuginfo" -print0 | xargs -0 rm
}

inherit update-alternatives

ALTERNATIVE_${JDKPN} = "java"
ALTERNATIVE_TARGET_${JDKPN} = "${JDK_HOME}/bin/java"

ALTERNATIVE_${JREPN} = "java"
ALTERNATIVE_TARGET_${JREPN} = "${JRE_HOME}/bin/java"

ALTERNATIVE_${JDKPN}-jdk = "javac"
ALTERNATIVE_TARGET_${JDKPN}-jdk = "${JDK_HOME}/bin/javac"

ALTERNATIVE_LINK_NAME[java] = "${bindir}/java"
ALTERNATIVE_LINK_NAME[javac] = "${bindir}/javac"
