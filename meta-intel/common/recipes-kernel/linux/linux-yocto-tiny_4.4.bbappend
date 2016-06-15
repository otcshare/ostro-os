FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

#LINUX_VERSION_i586-nlp-32-intel-common = "4.4.13"
SRCREV_meta_i586-nlp-32-intel-common = "870134f4bfa6208d6e5339e065486be3b6e693a5"
SRCREV_machine_i586-nlp-32-intel-common = "bc64c8124504681545cb97a22b69a4e4bfeb55e2"

COMPATIBLE_MACHINE_i586-nlp-32-intel-common = "${MACHINE}"
KBRANCH_i586-nlp-32-intel-common = "standard/tiny/intel/base"
KMACHINE_i586-nlp-32-intel-common = "intel-quark"
KERNEL_FEATURES_append_i586-nlp-32-intel-common = "${KERNEL_FEATURES_INTEL_COMMON}"
