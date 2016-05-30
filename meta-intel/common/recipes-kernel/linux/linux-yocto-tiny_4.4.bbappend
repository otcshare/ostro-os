FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

#LINUX_VERSION_i586-nlp-32-intel-common = "4.4.11"
SRCREV_meta_i586-nlp-32-intel-common = "3a5f494784591e01f0ae7ab748e8190582c16e8c"
SRCREV_machine_i586-nlp-32-intel-common = "53e84104c5e68eb468823dd0d262a64623d01a55"

COMPATIBLE_MACHINE_i586-nlp-32-intel-common = "${MACHINE}"
KBRANCH_i586-nlp-32-intel-common = "standard/tiny/intel"
KMACHINE_i586-nlp-32-intel-common = "intel-quark"
KERNEL_FEATURES_append_i586-nlp-32-intel-common = "${KERNEL_FEATURES_INTEL_COMMON}"
