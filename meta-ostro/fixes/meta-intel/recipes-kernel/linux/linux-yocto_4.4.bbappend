# Work around a build failure of 4.4.14 on intel-quark
# (https://bugzilla.yoctoproject.org/show_bug.cgi?id=9961)
# by freezing that machine on the previous kernel
# before meta-intel rev cb6b1f3f9.
LINUX_VERSION_INTEL_COMMON_intel-quark = "4.4.13"
SRCREV_META_INTEL_COMMON_intel-quark = "01ac19ede037b753d2b3f0adb20ab1becb7e1511"
SRCREV_MACHINE_INTEL_COMMON_intel-quark = "c49ed01a7e4c4fe9bfe4a4548480afd27d51088d"
