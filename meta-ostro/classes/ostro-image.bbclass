# Base class for Ostro images.

OSTRO_IMAGE_EXTRA_INSTALL ?= ""
IMAGE_INSTALL = " \
		kernel-modules \
		linux-firmware \
		packagegroup-core-boot \
                ${ROOTFS_PKGMANAGE_BOOTSTRAP} \
                ${CORE_IMAGE_EXTRA_INSTALL} \
                ${OSTRO_IMAGE_EXTRA_INSTALL} \
		"

# In Ostro OS, /bin/sh is always dash, even if bash is installed for
# interactive use.
IMAGE_INSTALL += "dash"

# Certain keywords, like "iotivity" are used in different contexts:
# - as image feature name
# - as bundle name
# - optional: as additional image suffix
#
# While this keeps the names short, it can also be a bit confusing and
# makes some of the definitions below look redundant. They are needed,
# though, because the naming convention could also be different.


# Image features sometimes affect image building (for example,
# ima enables image signing) and/or adds certain packages
# via FEATURE_PACKAGES.
#
# This is the list of image features which merely add packages.
#
# When using swupd bundles, each name here can be used to define a bundle,
# for example like this:
# SWUPD_BUNDLES = "tools-debug"
# BUNDLE_CONTENTS[tools-debug] = "${FEATURE_PACKAGES_tools-debug}"
OSTRO_IMAGE_PKG_FEATURES = " \
    app-framework \
    can \
    connectivity \
    devkit \
    iotivity \
    java-jdk \
    nodejs-runtime \
    nodejs-runtime-tools \
    python-runtime \
    qatests \
    soletta \
    tools-debug \
    tools-develop \
    tools-interactive \
"

# Here is the complete list of image features, also including
# those that modify the image configuration.
#
# TODO: document all relevant (not just IoT) image features
# in building-images.rst.
#
# swupd = install swupd client and enabled generation of swupd bundles
IMAGE_FEATURES[validitems] += " \
    autologin \
    muted \
    ima \
    smack \
    swupd \
    ${OSTRO_IMAGE_PKG_FEATURES} \
"

# An image derived from ostro-image.bbclass without additional configuration
# is very minimal. When building with swupd enabled, the content of the
# base image determines the "core-os" swupd bundle which contains the components
# which always must be present on a device.
#
# All additional components on top of the minimal ones defined by ostro-image.bbclass
# must be added explicitly by setting OSTRO_IMAGE_EXTRA_FEATURES or
# OSTRO_IMAGE_EXTRA_INSTALL (making them part of the core-os bundle when building
# with swupd and thus part of each image, or directly adding them to the image when
# building without swupd), or by defining additional bundles via
# SWUPD_BUNDLES.
IMAGE_FEATURES += " \
    ${@bb.utils.contains('DISTRO_FEATURES', 'ima', 'ima', '', d)} \
    ${@bb.utils.contains('DISTRO_FEATURES', 'smack', 'smack', '', d)} \
    ${OSTRO_IMAGE_EXTRA_FEATURES} \
"
OSTRO_IMAGE_EXTRA_FEATURES ?= ""
inherit ${@bb.utils.contains('IMAGE_FEATURES', 'swupd', 'swupd-image', '', d)}

# Make progress messages from do_swupd_update visible as normal command
# line output, instead of just recording it to the logs. Useful
# because that task can run for a long time without any output.
SWUPD_LOG_FN ?= "bbplain"

# When using the "swupd" image feature, ensure that OS_VERSION is
# set as intended. The default for local build works, but yields very
# unpredictable version numbers (see ostro.conf for details).
#
# For example, build with:
#   BB_ENV_EXTRAWHITE="$BB_ENV_EXTRAWHITE OS_VERSION" OS_VERSION=100 bitbake ostro-image-swupd
#   BB_ENV_EXTRAWHITE="$BB_ENV_EXTRAWHITE OS_VERSION" OS_VERSION=110 bitbake ostro-image-swupd
#   ...

# ostro-image.bbclass intentionally does not define any bundles.
# That belongs into image recipes, like the example ostro-image-swupd.bb.
#
# When building without swupd, choose which content is to be included
# in the image. See the example ostro-image-noswupd.bb.

# Customize priorities of alternative components. See ostro.conf.
#
# In general, Busybox or Toybox are preferred over alternatives.
# The expectation is that either Busybox or Toybox are used, but if
# both get installed, Toybox is used for those commands that it
# provides.
#
# It is still possible to build images with coreutils providing
# core system tools, one just has to remove Toybox/Busybox from
# the image.
export ALTERNATIVE_PRIORITY_BUSYBOX ?= "300"
export ALTERNATIVE_PRIORITY_TOYBOX ?= "301"
export ALTERNATIVE_PRIORITY_BASH ?= "305"

# Both systemd and the efi_combo_updater have problems when
# "mount" is provided by busybox: systemd fails to remount
# the rootfs read/write and the updater segfaults because
# it does not parse the output correctly.
#
# For now avoid these problems by sticking to the traditional
# mount utilities from util-linux.
export ALTERNATIVE_PRIORITY_UTIL_LINUX ?= "305"

# We do not know exactly which util-linux packages will get
# pulled into bundles, so we have to install all of them
# also in the os-core. Alternatively we could try to select
# just mount/umount as overrides for Toybox/Busybox.
IMAGE_INSTALL += "util-linux"

# We need "login" and "passwd" from shadow because:
# - Busybox "login" does not use PAM and thus would require
#   separate patching to support stateless motd (patched
#   in libpam); also the login via getty is different compared
#   to logins via ssh, which is potentially confusing and thus
#   should better be avoided (either no PAM, or PAM everywhere).
# - /dev/tty does not point to the serial console when logging
#   in via getty and using Busybox login, so anything that
#   tries to interact with the user (passwd, ssh) fails.
# - shadow "passwd" creates /etc/shadow if it does not exist
#   yet (required when setting the root password).
export ALTERNATIVE_PRIORITY_SHADOW ?= "305"
IMAGE_INSTALL += "shadow"

# Additional features and packages used in the base images of
# ostro-image-swupd.bb and ostro-image-noswupd.bb.
OSTRO_IMAGE_FEATURES_REFERENCE ?= " \
    connectivity \
    tools-interactive \
    ssh-server-openssh \
"
OSTRO_IMAGE_INSTALL_REFERENCE ?= ""

# Additional features and packages required to build something similar
# to the "dev" bundle in ostro-image-swupd.bb and thus
# ostro-image-swupd-dev.
OSTRO_IMAGE_FEATURES_DEV ?= " \
    ${OSTRO_IMAGE_PKG_FEATURES} \
    dev-pkgs \
"
OSTRO_IMAGE_INSTALL_DEV ?= ""

FEATURE_PACKAGES_app-framework = " \
    packagegroup-app-framework \
"

FEATURE_PACKAGES_connectivity = "packagegroup-core-connectivity"
FEATURE_PACKAGES_can = "packagegroup-core-can"

# "evmctl ima_verify <file>" can be used to check that a signed file is
# really unmodified.
FEATURE_PACKAGES_ima = "packagegroup-ima-evm-utils"

FEATURE_PACKAGES_iotivity = "packagegroup-iotivity"
FEATURE_PACKAGES_devkit = "packagegroup-devkit"

FEATURE_PACKAGES_nodejs-runtime = "packagegroup-nodejs-runtime"
FEATURE_PACKAGES_nodejs-runtime-tools = "packagegroup-nodejs-runtime-tools"
FEATURE_PACKAGES_python-runtime = "packagegroup-python-runtime"
FEATURE_PACKAGES_java-jdk = "packagegroup-java-jdk"
FEATURE_PACKAGES_soletta = "packagegroup-soletta"
FEATURE_PACKAGES_soletta-tools = "soletta-dev-app"

# git is not essential for compiling software, but include it anyway
# because it is the most common source code management tool.
FEATURE_PACKAGES_tools-develop = "packagegroup-core-buildessential git"

# Add bash because it is more convenient to use than dash.
# This does not change /bin/sh due to re-organized update-alternative
# priorities.
FEATURE_PACKAGES_tools-interactive = "packagegroup-tools-interactive bash"

# We could make bash the login shell for interactive accounts as shown
# below, but that would have to be done also in the os-core and thus
# tools-interactive would have to be set in all swupd images.
# TODO (?): introduce a bash-login-shell image feature?
# ROOTFS_POSTPROCESS_COMMAND_append = "${@bb.utils.contains('IMAGE_FEATURES', 'tools-interactive', ' root_bash_shell; ', '', d)}"
# root_bash_shell () {
#     sed -i -e 's;/bin/sh;/bin/bash;' \
#        ${IMAGE_ROOTFS}${sysconfdir}/passwd \
#        ${IMAGE_ROOTFS}${sysconfdir}/default/useradd
# }

FEATURE_PACKAGES_qatests = "packagegroup-qa-tests"

# Use gummiboot as the EFI bootloader.
EFI_PROVIDER = "gummiboot"

IMAGE_LINGUAS = " "

LICENSE = "MIT"

# See local.conf.sample for explanations.
OSTRO_ROOT_AUTHORIZED_KEYS ?= ""
ROOTFS_POSTPROCESS_COMMAND += "ostro_root_authorized_keys; "
ostro_root_authorized_keys () {
    mkdir ${IMAGE_ROOTFS}${ROOT_HOME}/.ssh
    echo "${OSTRO_ROOT_AUTHORIZED_KEYS}" >>${IMAGE_ROOTFS}${ROOT_HOME}/.ssh/authorized_keys
    chmod -R go-rwx ${IMAGE_ROOTFS}${ROOT_HOME}/.ssh
}

# Do not create ISO images by default, only HDDIMG will be created (if it gets created at all).
NOISO = "1"

# Add support for compressing images with zip. Works for arbitrary image
# types. Example: OSTRO_VM_IMAGE_TYPES = "dsk.zip dsk.vdi.zip"
COMPRESSIONTYPES_append = " zip"
ZIP_COMPRESSION_LEVEL ?= "-9"
COMPRESS_CMD_zip = "zip ${ZIP_COMPRESSION_LEVEL} ${IMAGE_NAME}${IMAGE_NAME_SUFFIX}.${type}.zip ${IMAGE_NAME}${IMAGE_NAME_SUFFIX}.${type}"
COMPRESS_DEPENDS_zip = "zip-native"

# Replace the default "live" (aka HDDIMG) images with whole-disk images
# XXX Drop the VM hack after taking care also of the non UEFI devices (those using U-Boot: edison and beaglebone)
OSTRO_VM_IMAGE_TYPES ?= "dsk dsk.vdi"
IMAGE_FSTYPES_remove_intel-core2-32 = "live"
IMAGE_FSTYPES_append_intel-core2-32 = " ${OSTRO_VM_IMAGE_TYPES}"
IMAGE_FSTYPES_remove_intel-corei7-64 = "live"
IMAGE_FSTYPES_append_intel-corei7-64 = " ${OSTRO_VM_IMAGE_TYPES}"
IMAGE_FSTYPES_remove_intel-quark = "live"
IMAGE_FSTYPES_append_intel-quark = " ${OSTRO_VM_IMAGE_TYPES}"

# Activate "dsk" image type.
IMAGE_CLASSES += "${@ 'image-dsk' if ${OSTRO_USE_DSK_IMAGES} else ''}"

# Inherit after setting variables that get evaluated when importing
# the classes. In particular IMAGE_FSTYPES is relevant because it causes
# other classes to be imported.

inherit core-image extrausers image-buildinfo

BUILD_ID ?= "${DATETIME}"
# Do not re-trigger builds just because ${DATETIME} changed.
BUILD_ID[vardepsexclude] += "DATETIME"
IMAGE_BUILDINFO_VARS_append = " BUILD_ID"

IMAGE_NAME = "${IMAGE_BASENAME}-${MACHINE}-${BUILD_ID}"

# Enable initramfs based on initramfs-framework (chosen in
# core-image-minimal-initramfs.bbappend). All machines must
# boot with a suitable initramfs, because IMA initialization is done
# in it.
OSTRO_INITRAMFS ?= "ostro-initramfs"
INITRD_IMAGE_intel-core2-32 = "${OSTRO_INITRAMFS}"
INITRD_IMAGE_intel-corei7-64 = "${OSTRO_INITRAMFS}"
INITRD_IMAGE_intel-quark = "${OSTRO_INITRAMFS}"

# The expected disk layout is not compatible with the HDD format:
# HDD places the rootfs as loop file in a VFAT partition (UEFI),
# while the rootfs is expected to be in its own partition.
NOHDD = "1"

# Image creation: add here the desired value for the PARTUUID of
# the rootfs. WARNING: any change to this value will trigger a
# rebuild (and re-sign, if enabled) of the combo EFI application.
ROOTFS_PARTUUID_VALUE = "12345678-9abc-def0-0fed-cba987654321"

# By default, all files will be signed. Once IMA is active and its
# policy includes a signed file, such signed files can be removed and
# replaced, but not modified. Therefore we have to exclude certain
# read/write files from signing and instead only hash them.
#
# To find such files, boot a signed image with no_ima, then run:
# cd /
# find etc usr -type f |
# while read i; do
#    ima=$(getfattr -d -e hex -m security.ima "$i" | grep security.ima)
#    if [ $(echo $ima | wc -c) -gt 60 ] ; then
#        if evmctl ima_verify "$i" >/dev/null; then
#            echo "Signature okay: $i"
#        else
#            echo "Broken signature: $i"
#        fi
#    elif [ -n "$ima" ]; then
#        if [ $(echo $ima | cut -c18-) = $(sha1sum "$i" | cut -c0-41) ]; then
#            echo "Hash okay: $i"
#        else
#            echo "Broken hash : $i"
#        fi
#    else
#        echo "Unprotected: $i"
#    fi
# done
#
# Files which get modified during booting will show up as "broken"
# or "unprotected".
#
# At the moment, Ostro OS sets up IMA so that everything must be either
# signed (thus becoming read-only) or hashed (writeable because the
# kernel will updated hashes). Everything under /etc, /var, /home and /usr/dbspace
# is writable. That policy gets loaded in the initramfs, see
# core-image-minimal-initramfs.bbappend.
#
# Common pitfalls:
# - After booting without IMA, enabling IMA again may run into problems
#   because files were modified without updating the hash. This can be
#   done manually with "evmctl ima_hash <file>".
# - rootfs must be mounted with "i_version" (see ima-evm-rootfs.bbclass for
#   more information). This is done via the "rootflags" boot parameter
#   (via APPEND) because only remounting like that via fstab is problematic
#   for those files written by systemd before remounting (/etc/machine-id!).
#   In addition, ima-evm-rootfs.bbclass also adds the parameter to the rootfs
#   because otherwise systemd would remove it.
# - When image signing is disabled, we must not load the IMA policy.
#   Alternatively, we could add a ostro-initramfs-noima, but the
#   benefits of that (smaller initramfs) do not justify the downsides
#   (building becomes slower).
OSTRO_WRITABLE_FILES = "-path './etc/*' -o -path './var/*' -o -path './home/*' -o -path './usr/dbspace/*'"
IMA_EVM_ROOTFS_SIGNED = ". -type f -a -uid 0 -a ! \( ${OSTRO_WRITABLE_FILES} \)"
IMA_EVM_ROOTFS_HASHED = ". -type f -a -uid 0 -a \( ${OSTRO_WRITABLE_FILES} \)"
IMA_EVM_ROOTFS_IVERSION = "/"
APPEND_append = "${@bb.utils.contains('IMAGE_FEATURES', 'ima', ' rootflags=i_version', ' no-ima', d)}"
# Conditionally including this class is problematic when manipulating the
# IMAGE_FEATURES after parsing the recipe, because then parsing will use
# the original value of IMAGE_FEATURES. Instead, we disable all operations
# by returning early from ima_evm_sign_rootfs.
inherit ima-evm-rootfs
ima_evm_sign_rootfs_prepend () {
    ${@bb.utils.contains('IMAGE_FEATURES', 'ima', '', 'return', d)}
}

# The logic for the "smack" image feature is reversed: when enabled,
# the boot parameters are not modified, which leads to "Smack is
# enabled". Removing the feature disables security and thus also
# Smack. This is relies on only supporting one MAC mechanism. Should
# we ever support more than one, the handling needs to be revised.
#
# When Smack is disabled via the distro feature, the image feature is
# also off, but security=none gets added anyway despite being redundant.
# It is kept as an additional indicator that the system boots without a MAC
# mechanism.
#
# The Edison BSP does not support APPEND, some other solution is needed
# for that machine.
APPEND_append = "${@bb.utils.contains('IMAGE_FEATURES', 'smack', '', ' security=none', d)}"

# In addition, when Smack is disabled in the image but enabled in the
# distro, we strip all Smack xattrs from the rootfs. Otherwise we still
# end up with Smack labels in the filesystem although we neither need
# nor want them, because the packages that were compiled for the distro
# have Smack enabled and will set the xattrs while getting installed.
ostro_image_strip_smack () {
    echo "Removing Smack xattrs:"
    set -e
    cd ${IMAGE_ROOTFS}
    find . -exec sh -c "getfattr -h -m ^security.SMACK.* '{}' | grep -q ^security" \; -print | while read path; do
        # Print removed Smack attributes to the log before removing them.
        getfattr -h -d -m ^security.SMACK.* "$path"
        getfattr -h -d -m ^security.SMACK.* "$path" | grep ^security | cut -d = -f1 | while read attr; do
           setfattr -h -x "$xattr" "$path"
        done
    done
}
OSTRO_IMAGE_STRIP_SMACK = "${@ 'ostro_image_strip_smack' if not bb.utils.contains('IMAGE_FEATURES', 'smack', True, False, d) and bb.utils.contains('DISTRO_FEATURES', 'smack', True, False, d) else '' }"
do_rootfs[postfuncs] += "${OSTRO_IMAGE_STRIP_SMACK}"
DEPENDS += "${@ 'attr-native' if '${OSTRO_IMAGE_STRIP_SMACK}' else '' }"

# Mount read-only at first. This gives systemd a chance to run fsck
# and then mount read/write.
APPEND_append = " ro"

# Ensure that images preserve Smack labels and IMA/EVM.
inherit xattr-images

# Create all users and groups normally created only at runtime already at build time.
inherit systemd-sysusers

# Provide an image feature that disables all consoles and makes
# journald mute.
python() {
    if bb.utils.contains('IMAGE_FEATURES', 'muted', True, False, d):
        import re

        # Mangle cmdline to drop all consoles and add quiet option
        cmdline = d.getVar('APPEND', True)
        new=re.sub('console=\w+(,\w*)*\s','', cmdline) + ' quiet'
        d.setVar('APPEND', new)
}

# In addition to cmdline mangling, make sure journal only gets
# emergency errors and any lower priority messages do not get
# logged. This is temporary approach and the cleanest way to disable
# logging (compared with removing the journald binary and related
# services here). Once the systemd recipe gives us better granulatiry
# for packaging, the preferred way to avoid logging is
# to not install systemd-journald at all.
ostro_image_muted () {
    sed -i -e 's/^#\(MaxLevelStore=\).*/\1emerg/'\
           -e 's/^\(ForwardToSyslog=yes\)/#\1/' \
           ${IMAGE_ROOTFS}${sysconfdir}/systemd/journald.conf

    # Remove systemd-getty-generator to avoid (serial-)getty services
    # being created for kernel detected consoles.
    rm ${IMAGE_ROOTFS}${systemd_unitdir}/system-generators/systemd-getty-generator

    # systemd installs getty@tty1.service by default so remove it too
    rm -r ${IMAGE_ROOTFS}${sysconfdir}/systemd/system/getty.target.wants
}
ROOTFS_POSTPROCESS_COMMAND += "${@bb.utils.contains('IMAGE_FEATURES', 'muted', 'ostro_image_muted;', '', d)}"

# Disable images that are unbuildable, with an explanation why.
# Attempts to build disabled images will show that explanation.
python () {
    if bb.utils.contains('IMAGE_FEATURES', 'ima', True, False, d):
        # This is not a complete sanity check, because which settings
        # are needed depends a lot on how signing is configured. But
        # IMA_EVM_X509 is always expected to be a valid file, so we
        # can test at least that.
        x509 = d.getVar('IMA_EVM_X509', True)
        import os
        if not os.path.isfile(x509):
            error = '''
IMA_EVM_X509 is not set to the name of an existing file.
Check whether IMA signing is configured correctly, see
doc/howtos/building-images.rst.

%s''' % '\n'.join(['%s = "%s"' % (x, d.getVar(x, True)) for x in ['IMA_EVM_KEY_DIR', 'IMA_EVM_PRIVKEY', 'IMA_EVM_X509', 'IMA_EVM_ROOT_CA']])
            # It would be neat to show also the unexpanded variable values,
            # but SkipRecipe or the code dumping it automatically expand
            # variables, so we cannot do that at the moment.
            raise bb.parse.SkipRecipe(error)
}

# Enable local auto-login of the root user (local = serial port and
# virtual console by default, can be configured).
OSTRO_LOCAL_GETTY ?= " \
    ${IMAGE_ROOTFS}${systemd_system_unitdir}/serial-getty@.service \
    ${IMAGE_ROOTFS}${systemd_system_unitdir}/getty@.service \
"
local_autologin () {
    sed -i -e 's/^\(ExecStart *=.*getty \)/\1--autologin root /' ${OSTRO_LOCAL_GETTY}
}
ROOTFS_POSTPROCESS_COMMAND += "${@bb.utils.contains('IMAGE_FEATURES', 'autologin', 'local_autologin;', '', d)}"

# Extends the /etc/motd message that is shown on each login.
# Normally it is empty.
OSTRO_EXTRA_MOTD ?= ""
python extra_motd () {
    with open(d.expand('${IMAGE_ROOTFS}${sysconfdir}/motd'), 'a') as f:
        f.write(d.getVar('OSTRO_EXTRA_MOTD', True))
}
ROOTFS_POSTPROCESS_COMMAND += "${@'extra_motd;' if d.getVar('OSTRO_EXTRA_MOTD', True) else ''}"

# Ensure that the os-release file contains values matching the current image creation build.
# We do not want to rebuild the the os-release package for that, because that would
# also trigger image rebuilds when nothing else changed.
ostro_image_patch_os_release () {
    sed -i \
        -e 's/distro-version-to-be-added-during-image-creation/${DISTRO_VERSION}/' \
        -e 's/build-id-to-be-added-during-image-creation/${BUILD_ID}/' \
        ${IMAGE_ROOTFS}/usr/lib/os-release
}
ostro_image_patch_os_release[vardepsexclude] = " \
    DISTRO_VERSION \
    BUILD_ID \
"
ROOTFS_POSTPROCESS_COMMAND += "ostro_image_patch_os_release; "

# The systemd-firstboot service makes no sense in Ostro. If it runs
# (apparently triggered by not having an /etc/machine-id), it asks
# interactively on the console for a default timezone and locale. We
# cannot rely on users answering these questions.
#
# Instead we pre-configure some defaults in the image and can remove
# the useless service.
ostro_image_disable_firstboot () {
    for i in /etc/systemd /lib/systemd /usr/lib/systemd /bin /usr/bin; do
        d="${IMAGE_ROOTFS}$i"
        if [ -d "$d" ] && [ ! -h "$d" ]; then
            for e in $(find "$d" -name systemd-firstboot.service -o -name systemd-firstboot.service.d -o -name systemd-firstboot); do
                echo "disable_firstboot: removing $e"
                rm -rf "$e"
            done
        fi
    done
}
ROOTFS_POSTPROCESS_COMMAND += "ostro_image_disable_firstboot; "
