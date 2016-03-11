DESCRIPTION = "Security manager and utilities"
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=86d3f3a95c324c9479bd8986968f4327;beginline=3"

inherit cmake

# Out-of-tree build is broken ("sqlite3 .security-manager.db <db.sql" where db.sql is in $S/db).
B = "${S}"

DEPENDS = " \
attr \
boost \
cynara \
icu \
libslp-db-util \
libcap \
smack \
sqlite3 \
sqlite3-native \
systemd \
tizen-platform-config \
"

PACKAGECONFIG ??= ""
PACKAGECONFIG[debug] = "-DCMAKE_BUILD_TYPE=DEBUG,-DCMAKE_BUILD_TYPE=RELEASE"

# TODO: get this from tizen-platform-config and adapt tizen-platform-config.
TZ_SYS_DB = "/usr/dbspace"

EXTRA_OECMAKE = " \
-DCMAKE_VERBOSE_MAKEFILE=ON \
-DVERSION=${PV} \
-DSYSTEMD_INSTALL_DIR=${systemd_unitdir}/system \
-DBIN_INSTALL_DIR=${bindir} \
-DDB_INSTALL_DIR=${TZ_SYS_DB} \
-DLIB_INSTALL_DIR=${libdir} \
-DSHARE_INSTALL_PREFIX=${datadir} \
-DINCLUDE_INSTALL_DIR=${includedir} \
"

inherit systemd
SYSTEMD_SERVICE_${PN} = "security-manager.service"

# The upstream source code contains the Tizen-specific policy configuration files.
# To replace them, create a security-manager.bbappend and set the following variable to a
# space-separated list of policy file names (not URIs!), for example:
# SECURITY_MANAGER_POLICY = "privilege-group.list usertype-system.profile"
#
# Leave it empty to use the upstream Tizen policy.
SECURITY_MANAGER_POLICY ?= ""
SRC_URI_append = " ${@' '.join(['file://' + x for x in d.getVar('SECURITY_MANAGER_POLICY', True).split()])}"
python do_patch_append () {
    import os
    import shutil
    import glob
    files = d.getVar('SECURITY_MANAGER_POLICY', True).split()
    if files:
        s = d.getVar('S', True)
        workdir = d.getVar('WORKDIR', True)
        for pattern in ['*.profile', '*.list']:
            for old_file in glob.glob(s + '/policy/' + pattern):
                os.unlink(old_file)
        for file in files:
            shutil.copy(file, s + '/policy')
}

do_install_append () {
   install -d ${D}/${systemd_unitdir}/system/multi-user.target.wants
   ln -s ../security-manager.service ${D}/${systemd_unitdir}/system/multi-user.target.wants/security-manager.service
   install -d ${D}/${systemd_unitdir}/system/sockets.target.wants
   ln -s ../security-manager.socket ${D}/${systemd_unitdir}/system/sockets.target.wants/security-manager.socket
}

RDEPENDS_${PN} += "smack"
pkg_postinst_${PN} () {
   set -e
   chsmack -a System $D${TZ_SYS_DB}/.security-manager.db
   chsmack -a System $D${TZ_SYS_DB}/.security-manager.db-journal
}

FILES_${PN} += " \
${systemd_unitdir} \
${TZ_SYS_DB} \
"

PACKAGES =+ "${PN}-policy"
FILES_${PN}-policy = " \
   ${datadir}/${PN} \
   ${bindir}/security-manager-policy-reload \
"
RDEPENDS_${PN}-policy += "sqlite3 cynara"
pkg_postinst_${PN}-policy () {
   if [ x"$D" = "x" ] && ${bindir}/security-manager-policy-reload; then
       exit 0
   else
       exit 1
   fi
}
