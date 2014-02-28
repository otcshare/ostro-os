require openjdk-6-release-6b24.inc

FILESPATH =. "${FILE_DIRNAME}/openjdk-6-6b27:"

EXTRA_OECONF += "--disable-downloading"

OPENJDK_VERSION = "b27"
OPENJDK_DATE = "26_oct_2012"
SRC_URI[openjdk.md5sum] = "3a0963158e07c8829c8bd31a698bd23d"
SRC_URI[openjdk.sha256sum] = "044c3877b15940ff04f8aa817337f2878a00cc89674854557f1a02f15b1802a0"

CACAO_VERSION = "68fe50ac34ec"
SRC_URI[cacao.md5sum] = "d7607c455d36ba69651dfea38546922c"
SRC_URI[cacao.sha256sum] = "b8230f20d7022f9230bbfea13b2f3f179b2f42db40138ac6d32c82fc418ffc3a"

JAMVM_VERSION = "0972452d441544f7dd29c55d64f1ce3a5db90d82"
SRC_URI[jamvm.md5sum] = "f4616713ec609e35aa8070811bd952aa"
SRC_URI[jamvm.sha256sum] = "bfa706402ac934d24f7119eb78f6be65e91439a4b2e49dbcc21e288137808f03"

JAXP_FILE = "jaxp144_04.zip"
SRC_URI[jaxp.md5sum] = "0ace787aa12177d201947e8ba0ba9bdd"
SRC_URI[jaxp.sha256sum] = "490f696218c1fed9cb180680af883fe309b414fec232e9cec19645e12ad0b43c"


ICEDTEAPATCHES += "file://icedtea-jdk-rmi-crosscompile.patch;apply=no \
                   file://icedtea-disable-sane-alsa.patch;apply=no \
                  "

DISTRIBUTION_PATCHES += "patches/icedtea-jdk-rmi-crosscompile.patch \
                         patches/icedtea-disable-sane-alsa.patch \
                        "
