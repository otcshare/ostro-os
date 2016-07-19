FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

#LINUX_VERSION_i586-nlp-32-intel-common = "4.1.27"
SRCREV_meta_i586-nlp-32-intel-common = "cab4fec4b7ab0efae0f44c1ec1836c035a9b78fe"
SRCREV_machine_i586-nlp-32-intel-common = "15cf090ded5157e67302313bff9da0fa056e8ea9"

COMPATIBLE_MACHINE_i586-nlp-32-intel-common = "${MACHINE}"
KBRANCH_i586-nlp-32-intel-common = "standard/tiny/intel/base"
KMACHINE_i586-nlp-32-intel-common = "intel-quark"
KERNEL_FEATURES_append_i586-nlp-32-intel-common = "${KERNEL_FEATURES_INTEL_COMMON}"
