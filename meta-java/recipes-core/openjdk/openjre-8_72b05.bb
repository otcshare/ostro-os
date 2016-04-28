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
    file://openjdk8-silence-d_fortify_source-warning.patch;apply=no \
"

do_install() {
    rm -rf ${D}${JRE_HOME}
    mkdir -p ${D}${JRE_HOME}
    cp -rp ${B}/images/j2re-image/* ${D}${JRE_HOME}
    chown -R root:root ${D}${JRE_HOME}
    install -m644 ${WORKDIR}/jvm.cfg  ${D}${JRE_HOME}/lib/${JDK_ARCH}/
    find ${D}${JRE_HOME} -name "*.debuginfo" -print0 | xargs -0 rm
}

FILES_${PN}_append = "\
    ${JRE_HOME}/bin/[a-z]* \
    ${JRE_HOME}/lib/[a-z]* \
    ${JRE_HOME}/LICENSE \
    ${JRE_HOME}/release \
"

FILES_${PN}-dbg_append = "\
    ${JRE_HOME}/bin/.debug/ \
    ${JRE_HOME}/lib/.debug/ \
    ${JRE_HOME}/lib/${JDK_ARCH}/.debug/ \
    ${JRE_HOME}/lib/${JDK_ARCH}/jli/.debug/ \
    ${JRE_HOME}/lib/${JDK_ARCH}/server/.debug/ \
"

FILES_${PN}-doc_append = "\
    ${JRE_HOME}/man \
    ${JRE_HOME}/ASSEMBLY_EXCEPTION \
    ${JRE_HOME}/THIRD_PARTY_README \
"

RPROVIDES_${PN} = "java2-vm"
PROVIDES_${PN} = "java2-vm"
RPROVIDES_${PN} = "java2-runtime"
PROVIDES_${PN} = "java2-runtime"

inherit update-alternatives

ALTERNATIVE_${PN} = "java"
ALTERNATIVE_LINK_NAME[java] = "${bindir}/java"
ALTERNATIVE_TARGET[java] = "${JRE_HOME}/bin/java"
ALTERNATIVE_PRIORITY[java] = "100"
