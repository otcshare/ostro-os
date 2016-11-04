FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

LINUX_VERSION_i586-nlp-32-intel-common = "4.1.33"
SRCREV_meta_i586-nlp-32-intel-common = "3c3197e65b6f2f5514853c1fe78ae8ffc131b02c"
SRCREV_machine_i586-nlp-32-intel-common = "6405a54f9904b3c5f756a6317da36549707d8291"

COMPATIBLE_MACHINE_i586-nlp-32-intel-common = "${MACHINE}"
KBRANCH_i586-nlp-32-intel-common = "standard/tiny/intel/base"
KMACHINE_i586-nlp-32-intel-common = "intel-quark"
KERNEL_FEATURES_append_i586-nlp-32-intel-common = "${KERNEL_FEATURES_INTEL_COMMON}"
