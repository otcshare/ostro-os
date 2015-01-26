require openjdk-6-release-6b27.inc

DEPENDS += "krb5 libxslt-native"

FILESPATH =. "${FILE_DIRNAME}/openjdk-6-6b32:"

ICEDTEAPATCHES += "file://icedtea-openjdk-remove-currency-data-generation-expi.patch;apply=no"

EXTRA_OECONF += "--disable-downloading \
                 --enable-system-zlib \
                 --enable-system-jpeg \
                 --enable-system-png \
                 --enable-system-gif \
                 --disable-system-lcms \
                "
do_configure_append () {
    patch -p0 <${WORKDIR}/icedtea-openjdk-remove-currency-data-generation-expi.patch
    cd openjdk-ecj
    patch -p1 <${WORKDIR}/icedtea-openjdk-remove-currency-data-generation-expi.patch
    cd ..
}

OPENJDK_VERSION = "b32"
OPENJDK_DATE = "15_jul_2014"
#https://java.net/projects/openjdk6/downloads/download/openjdk-6-src-b31-15_apr_2014.tar.gz
OPENJDK_URI = "https://java.net/projects/openjdk6/downloads/download/openjdk-6-src-${OPENJDK_VERSION}-${OPENJDK_DATE}.tar.gz;subdir=openjdk-src-dir;name=openjdk;unpack=false"
SRC_URI[openjdk.md5sum] = "a97c28256a61be76e3047c31e0349c04"
SRC_URI[openjdk.sha256sum] = "fe1eb7053fddfd325152f95f9719325e4ba67534a26fa690ca24fab75461a1fa"

JAMVM_VERSION = "ec18fb9e49e62dce16c5094ef1527eed619463aa"
SRC_URI[jamvm.md5sum] = "d50ae193d01a9251e10679c7a2cc6ff1"
SRC_URI[jamvm.sha256sum] = "31810266666c23822942aac62a78019c2c4589e1c5ee48329cbf42652d4437bc"

JAXP_FILE = "jaxp144_04.zip"
SRC_URI[jaxp.md5sum] = "0ace787aa12177d201947e8ba0ba9bdd"
SRC_URI[jaxp.sha256sum] = "490f696218c1fed9cb180680af883fe309b414fec232e9cec19645e12ad0b43c"
