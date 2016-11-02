FILESEXTRAPATHS_prepend := "${THISDIR}/gnu-efi:"
SRC_URI_append_intel-x86-common = "file://0001-Add-GUID-for-SMBIOS-3-entry-point-structure.patch"
PACKAGE_ARCH_intel-x86-common = "${INTEL_COMMON_PACKAGE_ARCH}"
