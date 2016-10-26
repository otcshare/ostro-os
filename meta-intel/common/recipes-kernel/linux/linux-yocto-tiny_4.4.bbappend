FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

LINUX_VERSION_i586-nlp-32-intel-common = "4.4.26"
SRCREV_meta_i586-nlp-32-intel-common = "3030330b066a33ce21164a8b30d0503cf9f68e5b"
SRCREV_machine_i586-nlp-32-intel-common = "4eb72141aa7c3b626a7fc42ae8da6f8b29e43a2c"

COMPATIBLE_MACHINE_i586-nlp-32-intel-common = "${MACHINE}"
KBRANCH_i586-nlp-32-intel-common = "standard/tiny/intel/base"
KMACHINE_i586-nlp-32-intel-common = "intel-quark"
KERNEL_FEATURES_append_i586-nlp-32-intel-common = "${KERNEL_FEATURES_INTEL_COMMON} cfg/fs/ext4.scc"
