FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

LINUX_VERSION_i586-nlp-32-intel-common = "4.8.3"
SRCREV_meta_i586-nlp-32-intel-common = "6d028d2818603cd82cfb707b3231b8a9038f13bb"
SRCREV_machine_i586-nlp-32-intel-common = "1adf9d36338dc3c63cdbf6f98bcbdc7bba42a794"

COMPATIBLE_MACHINE_i586-nlp-32-intel-common = "${MACHINE}"
KBRANCH_i586-nlp-32-intel-common = "standard/tiny/base"
KMACHINE_i586-nlp-32-intel-common = "intel-quark"

KERNEL_FEATURES_append_i586-nlp-32-intel-common = "${KERNEL_FEATURES_INTEL_COMMON} cfg/fs/ext4.scc"
