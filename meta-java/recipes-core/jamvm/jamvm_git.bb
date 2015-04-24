# Note: You *must* use this together with classpath-native 0.98.
# Otherwise it won't work!

require jamvm.inc

inherit distro_features_check

REQUIRED_DISTRO_FEATURES = "x11"

SRCREV = "6cef41d859fbc9ce7868a97cb2cb5dd2b10b9103"
PV = "2.0.0-devel+git${SRCPV}"

SRC_URI = "git://git.code.sf.net/p/jamvm/code;protocol=git \
           file://jamvm-jni_h-noinst.patch \
           file://libffi.patch \
           file://jamvm-minmax-heap.patch \
           file://java \
          "

S = "${WORKDIR}/git"

