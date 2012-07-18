# Note: You *must* use this together with classpath-native 0.98.
# Otherwise it won't work!

require jamvm.inc

SRCREV = "2fdfc86c4c52c14668bcb87fec8cd8ba87e24fc3"
PV = "1.5.5+1.6.0-devel+git${SRCPV}"

PR = "r3"

SRC_URI = "git://git.berlios.de/jamvm;protocol=git \
           file://jamvm-jni_h-noinst.patch \
           file://libffi.patch \
           file://jamvm-minmax-heap.patch \
          "

S = "${WORKDIR}/git"

