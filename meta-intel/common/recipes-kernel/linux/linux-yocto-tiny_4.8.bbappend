FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

LINUX_VERSION_i586-nlp-32-intel-common = "4.8"
SRCREV_meta_i586-nlp-32-intel-common = "6128a9e47cd1aeb46b604469c17bff3eba8d5f93"
SRCREV_machine_i586-nlp-32-intel-common = "67813e7efa3a4614e209c2f058d92ef9a636441a"

COMPATIBLE_MACHINE_i586-nlp-32-intel-common = "${MACHINE}"
KBRANCH_i586-nlp-32-intel-common = "standard/tiny/base"
KMACHINE_i586-nlp-32-intel-common = "intel-quark"

KERNEL_FEATURES_append_i586-nlp-32-intel-common = "${KERNEL_FEATURES_INTEL_COMMON} cfg/fs/ext4.scc"
