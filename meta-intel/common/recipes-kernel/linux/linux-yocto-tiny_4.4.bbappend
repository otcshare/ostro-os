FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

EXTRA_OEMAKE = "LD=${STAGING_BINDIR_NATIVE}/${HOST_SYS}/${TARGET_PREFIX}ld AR=${STAGING_BINDIR_NATIVE}/${HOST_SYS}/${TARGET_PREFIX}gcc-ar"

LINUX_VERSION_i586-nlp-32-intel-common = "4.4.56"
LINUX_VERSION_core2-32-intel-common = "4.4.56"
LINUX_VERSION_corei7-64-intel-common = "4.4.56"

SRCREV_meta_i586-nlp-32-intel-common = "271b0c8d5128f0cb18ed413cc59f683132ff8e3f"
SRCREV_meta_core2-32-intel-common = "271b0c8d5128f0cb18ed413cc59f683132ff8e3f"
SRCREV_meta_corei7-64-intel-common = "271b0c8d5128f0cb18ed413cc59f683132ff8e3f"

SRCREV_machine_i586-nlp-32-intel-common = "44f85874593099737459d586c85e411a43efd3c1"
SRCREV_machine_core2-32-intel-common = "44f85874593099737459d586c85e411a43efd3c1"
SRCREV_machine_corei7-64-intel-common = "44f85874593099737459d586c85e411a43efd3c1"

COMPATIBLE_MACHINE_i586-nlp-32-intel-common = "${MACHINE}"
COMPATIBLE_MACHINE_core2-32-intel-common = "${MACHINE}"
COMPATIBLE_MACHINE_corei7-64-intel-common = "${MACHINE}"

KBRANCH_i586-nlp-32-intel-common = "standard/tiny/intel/base"
KBRANCH_core2-32-intel-common = "standard/tiny/intel/base"
KBRANCH_corei7-64-intel-common = "standard/tiny/intel/base"

KMACHINE_i586-nlp-32-intel-common = "intel-quark"
KMACHINE_core2-32-intel-common = "intel-core2-32"
KMACHINE_corei7-64-intel-common = "intel-corei7-64"

KERNEL_FEATURES_append_i586-nlp-32-intel-common = "${KERNEL_FEATURES_INTEL_COMMON} cfg/fs/ext4.scc"
KERNEL_FEATURES_append_core2-32-intel-common = "${KERNEL_FEATURES_INTEL_COMMON} cfg/fs/ext4.scc"
KERNEL_FEATURES_append_corei7-64-intel-common = "${KERNEL_FEATURES_INTEL_COMMON} cfg/fs/ext4.scc"
