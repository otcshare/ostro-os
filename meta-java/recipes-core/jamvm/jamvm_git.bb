# Note: You *must* use this together with classpath-native 0.98.
# Otherwise it won't work!

require jamvm.inc

SRCREV = "ebd11bde0a97b57f0d18938c6b65468d3c932719"
PV = "1.5.5+1.6.0-devel+git${SRCPV}"

SRC_URI = "git://git.code.sf.net/p/jamvm/code;protocol=git \
           file://jamvm-jni_h-noinst.patch \
           file://libffi.patch \
           file://jamvm-minmax-heap.patch \
           file://java \
          "

S = "${WORKDIR}/git"

