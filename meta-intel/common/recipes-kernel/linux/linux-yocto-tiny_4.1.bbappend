FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

#LINUX_VERSION_i586-nlp-32-intel-common = "4.1.26"
SRCREV_meta_i586-nlp-32-intel-common = "9f68667031354532563766a3d04ca8a618e9177a"
SRCREV_machine_i586-nlp-32-intel-common = "9ba8c36e9ea7419d06accab5311e7fb0d56513ff"

COMPATIBLE_MACHINE_i586-nlp-32-intel-common = "${MACHINE}"
KBRANCH_i586-nlp-32-intel-common = "standard/tiny/intel/base"
KMACHINE_i586-nlp-32-intel-common = "intel-quark"
KERNEL_FEATURES_append_i586-nlp-32-intel-common = "${KERNEL_FEATURES_INTEL_COMMON}"
