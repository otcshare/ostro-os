SUMMARY = "Ostro OS Image."

OSTRO_IMAGE_EXTRA_INSTALL ?= ""
IMAGE_INSTALL = " \
		kernel-modules \
		linux-firmware \
		packagegroup-core-boot \
                ${ROOTFS_PKGMANAGE_BOOTSTRAP} \
                ${CORE_IMAGE_EXTRA_INSTALL} \
                ${OSTRO_IMAGE_EXTRA_INSTALL} \
		"

# Image features sometimes affect image building (for example,
# ima enables image signing) and/or adds certain packages
# via FEATURE_PACKAGES.
#
# TODO: document IoT specific image feature somewhere. Here?
IMAGE_FEATURES[validitems] += " \
    app-privileges \
    autologin \
    can \
    connectivity \
    devkit \
    ima \
    iotivity \
    java-jdk \
    node-runtime \
    python-runtime \
    qatests \
    smack \
    soletta \
    swupd \
    tools-develop \
"

# These features come from base recipes, but are not added to
# IMAGE_FEATURES[validitems]. Should better be fixed there.
IMAGE_FEATURES[validitems] += " \
    ptest-pkgs \
    ssh-server-openssh \
    tools-debug \
    tools-profile \
"

# Temporary variant for swupd.
# Currently swupd is not compatible with ima and smack,
# so disable them. This can be removed once they can coexist.
IMAGE_VARIANT[swupd] = " \
    no-smack \
    no-ima \
"

# Temporary variant for swupd.
# Currently swupd is not compatible with ima and smack,
# so disable them. This can be removed once they can coexist.
IMAGE_VARIANT[swupddev] = " \
    no-smack \
    no-ima \
    ptest-pkgs \
    tools-debug \
    tools-develop \
    tools-profile \
"

# "dev" images have the following features turned on.
# ptests are enabled because (platform) developers might want
# to run them and because it is a relatively small change which
# avoids unnecessary proliferation of image variations that
# need to be built automatically.
IMAGE_VARIANT[dev] = " \
    ptest-pkgs \
    tools-debug \
    tools-develop \
    tools-profile \
"

# "minimal" images are the opposite of the "dev" images:
# all non-essential features are turned off, while keeping
# security features turned on.
IMAGE_VARIANT[minimal] = " \
    no-can \
    no-devkit \
    no-iotivity \
    no-node-runtime \
    no-python-runtime \
    no-soletta \
    no-qatests \
    no-java-jdk \
    ${OSTRO_EXTRA_MINIMAL_IMAGE_FEATURES} \
"
OSTRO_EXTRA_MINIMAL_IMAGE_FEATURES ?= ""

# Default list of features in "ostro-image" images. Additional
# image variations modify this list, see BBCLASSEXTEND below.
# OSTRO_EXTRA_IMAGE_FEATURES can be used to add more features
# to the default list.
IMAGE_FEATURES += " \
                        can \
                        connectivity \
                        devkit \
                        ${@bb.utils.contains('DISTRO_FEATURES', 'ima', 'ima', '', d)} \
                        iotivity \
                        ssh-server-openssh \
                        node-runtime \
                        qatests \
                        python-runtime \
                        java-jdk \
                        soletta \
                        ${@bb.utils.contains('DISTRO_FEATURES', 'smack', 'smack', '', d)} \
                        swupd \
                        ${OSTRO_EXTRA_IMAGE_FEATURES} \
                        "
OSTRO_EXTRA_IMAGE_FEATURES ?= ""


# Create variants of the base recipe where certain features are
# turned on or off. The name of these modified recipes are
# ostro-image-<variant1>-<variant2>-..., for example:
#   ostro-image-dev
#   ostro-image-dev-noima (not enabled by default at the moment)
#
# These variants are created on-the-fly by the imagevariant.bbclass.
# Features preceeded by a "no" or "no-" are explicitly turned off.
# Features mentioned by name are turned on. All other features are on
# or off according to the original IMAGE_FEATURES list.
#
# Creating virtual recipes for all possible combinations of non-standard
# features leads to an increase in parsing time due to the combinatorial
# explosion. Therefore we define only those images that are both expected to
# be useful and (more important) supported. Users can still enable
# unsupported variations in the local.conf via OSTRO_EXTRA_IMAGE_VARIANTS.
OSTRO_EXTRA_IMAGE_VARIANTS ?= ""
BBCLASSEXTEND = " \
    imagevariant:dev \
    imagevariant:minimal \
    imagevariant:swupd \
    ${OSTRO_EXTRA_IMAGE_VARIANTS} \
"

# Once officially supported, variations with IMA disabled can be
# added. Right now, users need to do that in their local.conf:
# OSTRO_EXTRA_IMAGE_VARIANTS = "imagevariant:noima imagevariant:dev,noima"

# The AppFW depends on the security framework and user management, and these frameworks
# (currently?) make little sense without apps, therefore a single image feature is used
# for all of these.
FEATURE_PACKAGES_app-privileges = " \
    packagegroup-user-management \
    packagegroup-app-framework \
    packagegroup-security-framework \
"

FEATURE_PACKAGES_connectivity = "packagegroup-core-connectivity"
FEATURE_PACKAGES_can = "packagegroup-core-can"

# "evmctl ima_verify <file>" can be used to check that a signed file is
# really unmodified.
FEATURE_PACKAGES_ima = "packagegroup-ima-evm-utils"

FEATURE_PACKAGES_iotivity = "packagegroup-iotivity"
FEATURE_PACKAGES_devkit = "packagegroup-devkit"

FEATURE_PACKAGES_node-runtime = "packagegroup-node-runtime"
FEATURE_PACKAGES_python-runtime = "packagegroup-python-runtime"
FEATURE_PACKAGES_java-jdk = "packagegroup-java-jdk"
FEATURE_PACKAGES_soletta = "packagegroup-soletta"

# git is not essential for compiling software, but include it anyway
# because it is the most common source code management tool.
FEATURE_PACKAGES_tools-develop = "packagegroup-core-buildessential git"

FEATURE_PACKAGES_swupd = "packagegroup-swupd"

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

# Replace the default "live" (aka HDDIMG) images with whole-disk images
# XXX Drop the VM hack after taking care also of the non UEFI devices (those using U-Boot: edison and beaglebone)
OSTRO_VM_IMAGE_TYPES ?= "dsk dsk.xz dsk.vdi"
IMAGE_FSTYPES_remove_intel-core2-32 = "live"
IMAGE_FSTYPES_append_intel-core2-32 = " ${OSTRO_VM_IMAGE_TYPES}"
IMAGE_FSTYPES_remove_intel-corei7-64 = "live"
IMAGE_FSTYPES_append_intel-corei7-64 = " ${OSTRO_VM_IMAGE_TYPES}"
IMAGE_FSTYPES_remove_intel-quark = "live"
IMAGE_FSTYPES_append_intel-quark = " ${OSTRO_VM_IMAGE_TYPES}"

# Activate "dsk" image type.
# Currently this supports only EFI-based booting, so let's enable it only for the EFI platforms.
IMAGE_CLASSES += "${@bb.utils.contains_any('MACHINE', 'intel-core2-32 intel-corei7-64 intel-quark', 'image-dsk', '', d)}"

# Inherit after setting variables that get evaluated when importing
# the classes. In particular IMAGE_FSTYPES is relevant because it causes
# other classes to be imported.

inherit core-image extrausers image-buildinfo

BUILD_ID ?= "${DATETIME}"
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

# Exception for /usr/dbspace/.security-manager.db: we set the owner
# to a special "sqlite" user and then rely on the IMA policy only
# measuring/appraising files owned by root.
#
# SecurityManager is unaware of the change and does not need to
# care, because it runs as root and can thus still use the file.
# The file never gets removed either, so the change is permanent.
#
# That is necessary because IMA and sqlite do not play
# well together ("[Linux-ima-user] IMA hash update"). The problem
# is that the IMA hash only gets updated on close(), but sqlite
# and SecurityManager keep the file open unless SecurityManager shuts
# down. So a power loss after a write leads to an incorrect IMA hash
# and makes the .db file unusable.
#
# However, the .db.journal files still get created as root (and thus
# are owned by root) and suffer from the same risk. Both a setuid bit
# on the directory (not supported by Linux, only BSD) or gid support
# in IMA together with setgid (not in upstream kernel) would help, but
# as that doesn't work we have to accept a certain risk of corruption
# during the much smaller time window where these .db.journal files
# exist.
#
# Long term the right solution will be to limit IMA to the read-only
# rootfs and put all writeable files in a different partition.
inherit extrausers
EXTRA_USERS_PARAMS += " \
    useradd --system --home ${localstatedir}/lib/empty --no-create-home --shell /bin/false sqlite; \
"
ROOTFS_POSTPROCESS_COMMAND_append = "${@bb.utils.contains('IMAGE_FEATURES', 'app-privileges', ' set_sqlite_owner; ', '', d)}"
set_sqlite_owner () {
    # Both the groupadd and the security-manager postinst are expected
    # to have completed by now. If this command fails, something in
    # image creation regressed.
    chown sqlite "${IMAGE_ROOTFS}/usr/dbspace/.security-manager.db"
}

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

# Debug option:
# in case of problems during the transition from initramfs to rootfs, spawn a shell.
APPEND_append = " init_fatal_sh"

# Mount read-only at first. This gives systemd a chance to run fsck
# and then mount read/write.
APPEND_append = " ro"

# Ensure that images preserve Smack labels and IMA/EVM.
inherit xattr-images

# Create all users and groups normally created only at runtime already at build time.
inherit systemd-sysusers

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
