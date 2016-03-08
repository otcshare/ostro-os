FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

#LINUX_VERSION_i586-nlp-32-intel-common = "4.4.3"
SRCREV_meta-i586-nlp-32-intel-common = "8b6a7d80344837fd64163008521a31a6f891313e"
SRCREV_machine-i586-nlp-32-intel-common = "ff4c4ef15b51f45b9106d71bf1f62fe7c02e63c2"

COMPATIBLE_MACHINE_i586-nlp-32-intel-common = "${MACHINE}"
KBRANCH_i586-nlp-32-intel-common = "standard/tiny/common-pc"
KMACHINE_i586-nlp-32-intel-common = "intel-quark"
KERNEL_FEATURES_append_i586-nlp-32-intel-common = "${KERNEL_FEATURES_INTEL_COMMON}"
