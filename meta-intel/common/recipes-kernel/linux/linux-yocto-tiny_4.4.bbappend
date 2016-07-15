FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

#LINUX_VERSION_i586-nlp-32-intel-common = "4.4.14"
SRCREV_meta_i586-nlp-32-intel-common = "4800a400d5ace1d4332ee18b01ac1c680e454457"
SRCREV_machine_i586-nlp-32-intel-common = "8361321fec015bc3823d01dad25db7f3af31b6d5"

COMPATIBLE_MACHINE_i586-nlp-32-intel-common = "${MACHINE}"
KBRANCH_i586-nlp-32-intel-common = "standard/tiny/intel/base"
KMACHINE_i586-nlp-32-intel-common = "intel-quark"
KERNEL_FEATURES_append_i586-nlp-32-intel-common = "${KERNEL_FEATURES_INTEL_COMMON}"
