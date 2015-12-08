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
"

do_install() {
    do_install_jdk
}

PACKAGES_append = " \
    ${JDKPN}-demo-dbg \
    ${JDKPN}-demo \
    ${JDKPN}-source \
"

RPROVIDES_${JDKPN} = "java2-vm"
PROVIDES_${JDKPN} = "java2-vm"
RPROVIDES_${JDKPN} = "java2-runtime"
PROVIDES_${JDKPN} = "java2-runtime"

inherit update-alternatives

ALTERNATIVE_${PN} = "java"
ALTERNATIVE_LINK = "${bindir}/java"
ALTERNATIVE_TARGET = "${JDK_HOME}/bin/java"
ALTERNATIVE_PRIORITY = "100"

# PR = "${INC_PR}.1"
