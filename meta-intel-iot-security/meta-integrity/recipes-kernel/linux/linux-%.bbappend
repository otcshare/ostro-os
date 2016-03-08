IMA_ENABLED_HERE := "${@'yes' if bb.data.inherits_class('kernel', d) and 'ima' in d.getVar('DISTRO_FEATURES', True).split() else 'no'}"

IMA_FILESEXTRAPATHS_yes := "${THISDIR}/linux:"
IMA_FILESEXTRAPATHS_no := ""
FILESEXTRAPATHS_prepend := "${IMA_FILESEXTRAPATHS_${IMA_ENABLED_HERE}}"

# This patch is necessary to unpack archives with security.ima xattr
# such that security.ima is taken from the archive. If the policy
# allows hashing, unpatched kernels (at least up to 4.3) will replace
# a signed hash in security.ima with a locally computed hash.
#
# Note that only bsdtar/libarchive are known to work; GNU tar sets
# the security.ima on an empty file and the tries re-opening it for
# writing its content, which then fails due to the IMA hash mismatch.
#
# Patches are potentially kernel version specific. Only some tested kernel versions
# are supported here. Currently they all work with the same patch file, though.
IMA_EVM_SETATTR_PATCH_4.1.18 = "file://0001-ima-fix-ima_inode_post_setattr.patch"
IMA_EVM_SETATTR_PATCH_4.1.15 = "file://0001-ima-fix-ima_inode_post_setattr.patch"
IMA_EVM_SETATTR_PATCH_4.4.3 = "file://0001-ima-fix-ima_inode_post_setattr.patch"

# Kernel config fragment enabling IMA/EVM and (where necessary and possible)
# also patching the kernel.
IMA_EVM_CFG_yes = " file://ima.cfg \
                    ${@ d.getVar('IMA_EVM_SETATTR_PATCH_' + (d.getVar('LINUX_VERSION', True) or ''), True) or ''} \
                  "
IMA_EVM_CFG_no = ""
SRC_URI_append = "${IMA_EVM_CFG_${IMA_ENABLED_HERE}}"

# Put our x509 file into the build directory where the kernel
# compilation will find it automatically. We use the build
# directory because the source might be shared with
# other builds where we do not want this key.
#
# The IMA_EVM_ROOT_CA default is set globally in ima-evm-rootfs.bbclass.
# Need weaker default here in case that ima-evm-rootfs.bbclass is not
# inherited.
IMA_EVM_ROOT_CA ??= ""
do_compile_ima_evm_yes = "    [ '${IMA_EVM_ROOT_CA}' ] && cp '${IMA_EVM_ROOT_CA}' '${B}'"
do_compile_ima_evm_no = ":"

do_compile_prepend () {
${do_compile_ima_evm_${IMA_ENABLED_HERE}}
}
