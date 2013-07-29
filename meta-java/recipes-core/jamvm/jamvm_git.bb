# Note: You *must* use this together with classpath-native 0.98.
# Otherwise it won't work!

require jamvm.inc

SRCREV = "ac22c9948434e528ece451642b4ebde40953ee7e"
PV = "1.5.5+1.6.0-devel+git${SRCPV}"

SRC_URI = "git://git.berlios.de/jamvm;protocol=git \
           file://jamvm-jni_h-noinst.patch \
           file://libffi.patch \
           file://jamvm-minmax-heap.patch \
           file://annotations.patch \
           file://java \
          "

S = "${WORKDIR}/git"

