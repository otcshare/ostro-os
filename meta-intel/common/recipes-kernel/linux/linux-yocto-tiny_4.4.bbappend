FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

#LINUX_VERSION_i586-nlp-32-intel-common = "4.4.11"
SRCREV_meta_i586-nlp-32-intel-common = "1465ac389f22979618852aa04298049cfdd5dcb4"
SRCREV_machine_i586-nlp-32-intel-common = "628bf627561c6285d99fb978e11d4c15fc29324b"

COMPATIBLE_MACHINE_i586-nlp-32-intel-common = "${MACHINE}"
KBRANCH_i586-nlp-32-intel-common = "standard/tiny/intel"
KMACHINE_i586-nlp-32-intel-common = "intel-quark"
KERNEL_FEATURES_append_i586-nlp-32-intel-common = "${KERNEL_FEATURES_INTEL_COMMON}"
