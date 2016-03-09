FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

#LINUX_VERSION_i586-nlp-32-intel-common = "4.4.1"
SRCREV_meta-i586-nlp-32-intel-common = "4940c6e551c1eea41a5dbc69a90b23d5f835fa5b"
SRCREV_machine-i586-nlp-32-intel-common = "0194c765861157b95de80fa7c27ebb6b51c16dd6"

COMPATIBLE_MACHINE_i586-nlp-32-intel-common = "${MACHINE}"
KBRANCH_i586-nlp-32-intel-common = "standard/tiny/common-pc"
KMACHINE_i586-nlp-32-intel-common = "intel-quark"
KERNEL_FEATURES_append_i586-nlp-32-intel-common = "${KERNEL_FEATURES_INTEL_COMMON}"
