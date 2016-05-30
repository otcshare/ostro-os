FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

#LINUX_VERSION_i586-nlp-32-intel-common = "4.1.24"
SRCREV_meta_i586-nlp-32-intel-common = "4b4199bd24f206d459061bb0a920d009429d5ed3"
SRCREV_machine_i586-nlp-32-intel-common = "403eda4633e9037fb715d0d1e8ae847b2bd0651a"

COMPATIBLE_MACHINE_i586-nlp-32-intel-common = "${MACHINE}"
KBRANCH_i586-nlp-32-intel-common = "standard/tiny/intel"
KMACHINE_i586-nlp-32-intel-common = "intel-quark"
KERNEL_FEATURES_append_i586-nlp-32-intel-common = "${KERNEL_FEATURES_INTEL_COMMON}"
