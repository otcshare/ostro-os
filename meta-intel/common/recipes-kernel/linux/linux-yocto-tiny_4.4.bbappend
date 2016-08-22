FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

#LINUX_VERSION_i586-nlp-32-intel-common = "4.4.18"
SRCREV_meta_i586-nlp-32-intel-common = "6a12efcabe8d48e323afd277fa672eae9b7e12c2"
SRCREV_machine_i586-nlp-32-intel-common = "138ddb9e0afaeb37c78146f2f43f927885e94ec7"

COMPATIBLE_MACHINE_i586-nlp-32-intel-common = "${MACHINE}"
KBRANCH_i586-nlp-32-intel-common = "standard/tiny/intel/base"
KMACHINE_i586-nlp-32-intel-common = "intel-quark"
KERNEL_FEATURES_append_i586-nlp-32-intel-common = "${KERNEL_FEATURES_INTEL_COMMON}"
