require openjdk-8-release-72b05.inc
require openjdk-8-cross.inc

# some patches extracted from http://cr.openjdk.java.net/~rkennke/shark-build-hotspot/webrev.01/hotspot.patch
# reported via http://mail.openjdk.java.net/pipermail/build-dev/2015-January/013972.html
# by Roman Kennke (rkennke at redhat.com)
PATCHES_URI_append = "\
    file://openjdk8-restrict-to-staging-dir.patch;apply=no \
    file://openjdk8-fix-shark-build.patch;apply=no \
    file://openjdk8-fix-shark-stdc++11.patch;apply=no \
    file://openjdk8-use_builtin_frame_address_0_rather_than_returning_address_of_local_variable.patch;apply=no \
    file://openjdk8-fix-assembler-flag-handling-in-makefile.patch;apply=no \
    file://openjdk8-fix-adlc-flags.patch;apply=no \
    file://openjdk8-silence-d_fortify_source-warning.patch;apply=no \
"

do_install() {
    rm -rf ${D}${JDK_HOME}
    mkdir -p ${D}${JDK_HOME}
    cp -rp ${B}/images/j2sdk-image/* ${D}${JDK_HOME}
    chown -R root:root ${D}${JDK_HOME}
    install -m644 ${WORKDIR}/jvm.cfg  ${D}${JDK_HOME}/jre/lib/${JDK_ARCH}/
    find ${D}${JDK_HOME} -name "*.debuginfo" -print0 | xargs -0 rm
}

PACKAGES_append = " \
    ${PN}-demo-dbg \
    ${PN}-demo \
    ${PN}-source \
"

FILES_${PN}_append = "\
    ${JDK_HOME}/bin/[a-z]* \
    ${JDK_HOME}/lib/[a-z]* \
    ${JDK_HOME}/jre/bin/[a-z]* \
    ${JDK_HOME}/jre/lib/[a-z]* \
    ${JDK_HOME}/LICENSE \
    ${JDK_HOME}/jre/LICENSE \
    ${JDK_HOME}/release \
"

FILES_${PN}-dev_append = "\
    ${JDK_HOME}/include \
"

FILES_${PN}-dbg_append = "\
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

FILES_${PN}-demo = " ${JDK_HOME}/demo ${JDK_HOME}/sample "
RDEPENDS_${PN}-demo = " ${PN} "

FILES_${PN}-demo-dbg = "\
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

FILES_${PN}-doc_append = "\
    ${JDK_HOME}/man \
    ${JDK_HOME}/ASSEMBLY_EXCEPTION \
    ${JDK_HOME}/THIRD_PARTY_README \
    ${JDK_HOME}/jre/ASSEMBLY_EXCEPTION \
    ${JDK_HOME}/jre/THIRD_PARTY_README \
    ${JDK_HOME}/man \
"

FILES_${PN}-source = " ${JDK_HOME}/src.zip "

RPROVIDES_${PN} = "java2-vm"
PROVIDES_${PN} = "java2-vm"
RPROVIDES_${PN} = "java2-runtime"
PROVIDES_${PN} = "java2-runtime"

inherit update-alternatives

ALTERNATIVE_PRIORITY = "100"

ALTERNATIVE_${PN} = "java javac"
ALTERNATIVE_LINK_NAME[java] = "${bindir}/java"
ALTERNATIVE_TARGET[java] = "${JDK_HOME}/bin/java"

ALTERNATIVE_LINK_NAME[javac] = "${bindir}/javac"
ALTERNATIVE_TARGET[javac] = "${JDK_HOME}/bin/javac"
