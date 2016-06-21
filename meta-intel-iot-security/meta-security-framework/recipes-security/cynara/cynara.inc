DESCRIPTION = "Cynara service with client libraries"
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=86d3f3a95c324c9479bd8986968f4327;beginline=3"

DEPENDS = " \
dbus \
glib-2.0 \
systemd \
zip \
"

# For testing:
# DEPENDS += "gmock"

PACKAGECONFIG ??= ""
# Use debug mode to increase logging. Beware, also compiles with less optimization
# and thus has to disable FORTIFY_SOURCE below.
PACKAGECONFIG[debug] = "-DCMAKE_BUILD_TYPE=DEBUG,-DCMAKE_BUILD_TYPE=RELEASE,libunwind elfutils"

inherit cmake

CXXFLAGS_append = " \
-DCYNARA_STATE_PATH=\\\\\"${localstatedir}/cynara/\\\\\" \
-DCYNARA_LIB_PATH=\\\\\"${prefix}/lib/cynara/\\\\\" \
-DCYNARA_TESTS_DIR=\\\\\"${prefix}/share/cynara/tests/\\\\\" \
-DCYNARA_CONFIGURATION_DIR=\\\\\"${sysconfdir}/cynara/\\\\\" \
-DCYNARA_VERSION=\\\\\"${PV}\\\\\" \
${@bb.utils.contains('PACKAGECONFIG', 'debug', '-Wp,-U_FORTIFY_SOURCE', '', d)} \
"

EXTRA_OECMAKE += " \
-DCMAKE_VERBOSE_MAKEFILE=ON \
-DSYSTEMD_SYSTEM_UNITDIR=${systemd_unitdir}/system \
-DLIB_INSTALL_DIR=${libdir} \
-DBIN_INSTALL_DIR=${bindir} \
-DSBIN_INSTALL_DIR=${sbindir} \
-DINCLUDE_INSTALL_DIR=${includedir} \
"

# Explicitly package empty directory. Otherwise Cynara prints warnings
# at runtime:
# cyad[198]: Couldn't scan for plugins in </usr/lib/cynara/plugin/service/> : <No such file or directory>
FILES_${PN}_append = " \
${libdir}/cynara/plugin/service \
${libdir}/cynara/plugin/client \
"

# Testing depends on gmock and gtest. They can be found in meta-oe
# and are not necessarily available, so this feature is off by default.
# If gmock from meta-oe is used, then a workaround is needed to avoid
# a link error (libgmock.a calls pthread functions without libpthread
# being listed in the .pc file).
PACKAGECONFIG[tests] = "-DBUILD_TESTS:BOOL=ON,-DBUILD_TESTS:BOOL=OFF,gmock gtest,"
SRC_URI_append = "${@bb.utils.contains('PACKAGECONFIG', 'tests', ' file://gmock-pthread-linking.patch file://run-ptest', '', d)}"

# Will be empty if no tests were built.
inherit ptest
FILES_${PN}-ptest += "${bindir}/cynara-tests ${bindir}/cynara-db-migration-tests ${datadir}/cynara/tests"
do_install_ptest () {
    if ${@bb.utils.contains('PACKAGECONFIG', 'tests', 'true', 'false', d)}; then
        mkdir -p ${D}/${datadir}/cynara/tests
        cp -r ${S}/test/db/* ${D}/${datadir}/cynara/tests
    fi
}

do_compile_prepend () {
    # en_US.UTF8 is not available, causing cynara-tests parser.getKeyAndValue to fail.
    # Submitted upstream: https://github.com/Samsung/cynara/issues/10
    sed -i -e 's/std::locale("en_US.UTF8")/std::locale::classic()/g' ${S}/test/credsCommons/parser/Parser.cpp
}

inherit useradd
USERADD_PACKAGES = "${PN}"
GROUPADD_PARAM_${PN} = "-r cynara"
USERADD_PARAM_${PN} = "\
--system --home ${localstatedir}/lib/empty \
--no-create-home --shell /bin/false \
--gid cynara cynara \
"

# Causes deadlock during booting, see workaround in postinst below.
#inherit systemd
#SYSTEMD_SERVICE_${PN} = "cynara.service"

do_install_append () {
   chmod a+rx ${D}/${sbindir}/cynara-db-migration

   install -d ${D}${sysconfdir}/cynara/
   install -m 644 ${S}/conf/creds.conf ${D}/${sysconfdir}/cynara/creds.conf

   # No need to create empty directories except for those which
   # Cynara expects to find.
   # install -d ${D}${localstatedir}/cynara/
   # install -d ${D}${prefix}/share/cynara/tests/empty_db
   install -d ${D}${libdir}/cynara/plugin/client
   install -d ${D}${libdir}/cynara/plugin/service

   # install db* ${D}${prefix}/share/cynara/tests/

   install -d ${D}${systemd_unitdir}/system/sockets.target.wants
   ln -s ../cynara.socket ${D}${systemd_unitdir}/system/sockets.target.wants/cynara.socket
   ln -s ../cynara-admin.socket ${D}${systemd_unitdir}/system/sockets.target.wants/cynara-admin.socket
   ln -s ../cynara-agent.socket ${D}${systemd_unitdir}/system/sockets.target.wants/cynara-agent.socket
}

FILES_${PN} += "${systemd_unitdir}/system"

# Cynara itself has no dependency on Smack. Only its installation
# is Smack-aware in the sense that it sets Smack labels. Do not
# depend on smack userspace unless we really need Smack labels.
#
# The Tizen .spec file calls cynara-db-migration in a %pre section.
# That only works when cynara-db-migration is packaged separately
# (overly complex) and does not seem necessary: perhaps there is a
# time window where cynara might already get activated before
# the postinst completes, but that is a general problem. It gets
# avoided entirely when calling this script while building the
# rootfs.
RDEPENDS_${PN}_append_smack = " smack-userspace"
DEPENDS_append_smack = " smack-userspace-native"
CHSMACK_smack = "chsmack"
CHSMACK = "true"
pkg_postinst_${PN} () {
   # Fail on error.
   set -e

   # It would be nice to run the code below while building an image,
   # but currently the calls to cynara-db-chsgen (a binary) in
   # cynara-db-migration (a script) prevent that. Rely instead
   # on OE's support for running failed postinst scripts at first boot.
   if [ x"$D" != "x" ]; then
      exit 1
   fi

   mkdir -p $D${sysconfdir}/cynara
   ${CHSMACK} -a System $D${sysconfdir}/cynara

   # Strip git patch level information, the version comparison code
   # in cynara-db-migration only expect major.minor.patch version numbers.
   VERSION=${@bb.data.getVar('PV',d,1).split('+git')[0]}
   if [ -d $D${localstatedir}/cynara ] ; then
      # upgrade
      echo "NOTE: updating cynara DB to version $VERSION"
      $D${sbindir}/cynara-db-migration upgrade -f 0.0.0 -t $VERSION
   else
      # install
      echo "NOTE: creating cynara DB for version $VERSION"
      mkdir -p $D${localstatedir}/cynara
      ${CHSMACK} -a System $D${localstatedir}/cynara
      $D${sbindir}/cynara-db-migration install -t $VERSION
   fi

   # Workaround for systemd.bbclass issue: it would call
   # "systemctl start" without "--no-block", but because
   # the service is not ready to run at the time when
   # this scripts gets executed by run-postinsts.service,
   # booting deadlocks.
   echo "NOTE: enabling and starting cynara service"
   systemctl enable cynara
   systemctl start --no-block cynara
}
