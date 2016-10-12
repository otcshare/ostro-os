FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

LINUX_VERSION_i586-nlp-32-intel-common = "4.8"
SRCREV_meta_i586-nlp-32-intel-common = "552a83790b1797b6dd4e4c48ff5bc8f215ed57da"
SRCREV_machine_i586-nlp-32-intel-common = "67813e7efa3a4614e209c2f058d92ef9a636441a"

COMPATIBLE_MACHINE_i586-nlp-32-intel-common = "${MACHINE}"
KBRANCH_i586-nlp-32-intel-common = "standard/tiny/base"
KMACHINE_i586-nlp-32-intel-common = "intel-quark"

KERNEL_FEATURES_append_i586-nlp-32-intel-common = "${KERNEL_FEATURES_INTEL_COMMON} cfg/fs/ext4.scc"
