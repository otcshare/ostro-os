IMA_ENABLED_HERE := "${@'yes' if bb.data.inherits_class('kernel', d) and 'ima' in d.getVar('DISTRO_FEATURES', True).split() else 'no'}"

IMA_FILESEXTRAPATHS_yes := "${THISDIR}/linux:"
IMA_FILESEXTRAPATHS_no := ""
FILESEXTRAPATHS_prepend := "${IMA_FILESEXTRAPATHS_${IMA_ENABLED_HERE}}"

# These two patches are necessary to unpack archives with security.ima xattr
# such that security.ima is taken from the archive. If the policy
# allows hashing, unpatched kernels (at least up to 4.3) will replace
# a signed hash in security.ima with a locally computed hash.
#
# Note that only bsdtar/libarchive are known to work; GNU tar sets
# the security.ima on an empty file and the tries re-opening it for
# writing its content, which then fails due to the IMA hash mismatch.
#
# Kernels >= 4.7 have the patches, while older kernels are likely to
# need the patches. So apply them by default. To avoid that,
# set IMA_EVM_SETATTR_PATCH_x.y.z (where x.y.z == linux kernel version)
# to an empty string (to avoid patching) or some other patch files
# suitable for that kernel.
def ima_evm_setattr_patch(d):
    result = []
    linux_version = d.getVar('LINUX_VERSION', True) or ''
    # These two patches are known to be included upstream.
    if bb.utils.vercmp_string_op(linux_version, '4.7', '<'):
        patches = d.getVar('IMA_EVM_SETATTR_PATCH_' + linux_version, True)
        if patches != None:
            # Patches explicitly chosen, may be empty.
            result.append(patches)
        else:
            # Enabled by default.
            result.append('file://0001-ima-fix-ima_inode_post_setattr.patch file://0002-ima-add-support-for-creating-files-using-the-mknodat.patch')
    # This one addresses a problem added in 4.2. The upstream revert will land
    # in some future kernel. We need to extend version check once we know
    # which kernels have the patch.
    if bb.utils.vercmp_string_op(linux_version, '4.2', '>='):
        patches = d.getVar('IMA_EVM_SETATTR_REVERT_PATCH_' + linux_version, True)
        if patches != None:
            # Patches explicitly chosen, may be empty.
            result.append(patches)
        else:
            # Enabled by default.
            result.append('file://Revert-ima-limit-file-hash-setting-by-user-to-fix-an.patch')
    return ' '.join(result)

# Edison kernel too old, patch not applicable -> swupd is broken in Ostro OS for Edison.
IMA_EVM_SETATTR_PATCH_3.10.98 = ""

# Kernel config fragment enabling IMA/EVM and (where necessary and possible)
# also patching the kernel.
IMA_EVM_CFG_yes = " file://ima.cfg \
                    ${@ ima_evm_setattr_patch(d)} \
                  "
IMA_EVM_CFG_no = ""
SRC_URI_append = "${IMA_EVM_CFG_${IMA_ENABLED_HERE}}"

# IMA_EVM_ROOT_CA, if set, is the absolute path to a der-encoded
# x509 CA certificate which will get compiled into the kernel.
# The kernel will then use it to validate additional certificates,
# like the one loaded dynamically for IMA.
#
# Depending on the kernel version, there are two ways to add the
# CA certificate:
# - For Linux < 4.3, we put the x509 file into the source directory
#   where the kernel compilation will find it automatically
#   (http://lxr.free-electrons.com/source/kernel/Makefile?v=4.2#L115).
# - For Linux >= 4.3, we set SYSTEM_TRUSTED_KEYS
#   (http://lxr.free-electrons.com/source/certs/Kconfig?v=4.3#L29).
#   The ima_evm_root_ca.cfg only contains a blank file name.
#   The actual file name gets patched in after the file was used
#   to configure the kernel (see do_kernel_configme_append).
#   This has to point to a single file, i.e. using it for IMA has to
#   be coordinated with other usages.
#
# The IMA_EVM_ROOT_CA default is set globally in ima-evm-rootfs.bbclass.
# Need weaker default here in case that ima-evm-rootfs.bbclass is not
# inherited.
IMA_EVM_ROOT_CA ??= ""

# Add CONFIG_SYSTEM_TRUSTED_KEYS (for recent kernels) and
# copy the root certificate into the build directory. By using
# the normal fetcher mechanism for the certificate we ensure that
# a rebuild is triggered when the file name or content change.
#
# Recompiling on name change is a bit too aggressive and causes
# unnecessary rebuilds when only the location of the file, but not its
# content change. This may need further work, should it become a problem
# in practice. For example, IMA_EVM_ROOT_CA could be redefined as
# an URL that then gets found via the normal file lookup.
#
# The fetcher does not expand SRC_URI. We have to enforce that here.
IMA_EVM_ROOT_CA_CFG_yes = "${@ \
 ((' file://ima_evm_root_ca.cfg' if bb.utils.vercmp_string_op('${LINUX_VERSION}', '4.3', '>=') else '') + \
   ' file://${IMA_EVM_ROOT_CA}') \
 if '${IMA_EVM_ROOT_CA}' else ''}"
IMA_EVM_ROOT_CA_CFG_no = ""

SRC_URI_append = "${IMA_EVM_ROOT_CA_CFG_${IMA_ENABLED_HERE}}"

do_kernel_configme_append () {
    if [ '${IMA_EVM_ROOT_CA}' ] && grep -q '^CONFIG_SYSTEM_TRUSTED_KEYS=' ${B}/.config; then
        # We can replace a blank value from ima_evm_root_ca.cfg,
        # but when we find some other value, then we have to abort
        # because we can't set more than one value.
        eval `grep '^CONFIG_SYSTEM_TRUSTED_KEYS='`
        if [ "$CONFIG_SYSTEM_TRUSTED_KEYS" ] && [ "$CONFIG_SYSTEM_TRUSTED_KEYS" != "${IMA_EVM_ROOT_CA}" ]; then
            bbfatal "CONFIG_SYSTEM_TRUSTED_KEYS already set to $CONFIG_SYSTEM_TRUSTED_KEYS, cannot replace with IMA_EVM_ROOT_CA = ${IMA_EVM_ROOT_CA}"
            exit 1
        fi
        pemcert=${B}/`basename ${IMA_EVM_ROOT_CA}`.pem
        openssl x509 -inform der -in ${IMA_EVM_ROOT_CA} -out $pemcert
        sed -i -e "s;^CONFIG_SYSTEM_TRUSTED_KEYS=.*;CONFIG_SYSTEM_TRUSTED_KEYS=\"$pemcert\";" ${B}/.config
    fi
}

do_kernel_configme[depends] += "${@ 'openssl-native:do_populate_sysroot' if '${IMA_ENABLED_HERE}' == 'yes' and '${IMA_EVM_ROOT_CA}' else '' }"
