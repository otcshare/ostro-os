FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

LINUX_VERSION_i586-nlp-32-intel-common = "4.1.38"
SRCREV_meta_i586-nlp-32-intel-common = "7140ddb86e4b01529185e6d4a606001ad152b8f3"
SRCREV_machine_i586-nlp-32-intel-common = "b3744106e406887989a8bb4695480e7f3cdd36cb"

COMPATIBLE_MACHINE_i586-nlp-32-intel-common = "${MACHINE}"
KBRANCH_i586-nlp-32-intel-common = "standard/tiny/intel/base"
KMACHINE_i586-nlp-32-intel-common = "intel-quark"
KERNEL_FEATURES_append_i586-nlp-32-intel-common = "${KERNEL_FEATURES_INTEL_COMMON}"
