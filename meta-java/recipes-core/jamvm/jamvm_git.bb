# Note: You *must* use this together with classpath-native 0.98.
# Otherwise it won't work!

require jamvm.inc

SRCREV = "0972452d441544f7dd29c55d64f1ce3a5db90d82"
PV = "1.5.5+1.6.0-devel+git${SRCPV}"

PR = "r4"

SRC_URI = "git://git.berlios.de/jamvm;protocol=git \
           file://jamvm-jni_h-noinst.patch \
           file://libffi.patch \
           file://jamvm-minmax-heap.patch \
          "

S = "${WORKDIR}/git"

