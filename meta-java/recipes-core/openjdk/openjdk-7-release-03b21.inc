require openjdk-7-common.inc

LIC_FILES_CHKSUM = "file://COPYING;md5=59530bdf33659b29e73d4adb9f9f6552"

FILESPATH =. "${FILE_DIRNAME}/openjdk-7-03b21:"

# Name of the directory containing the compiled output
BUILD_DIR = "openjdk.build"
BUILD_DIR_ECJ = "openjdk.build-ecj"

# Force arm mode for now
ARM_INSTRUCTION_SET_armv4t = "ARM"

ICEDTEA_URI = "http://icedtea.classpath.org/download/source/${ICEDTEA}.tar.gz;name=iced"

ICEDTEA_PREFIX = "icedtea7-forest-2.1"
ICEDTEA_HG_URL = "http://icedtea.classpath.org/hg/release/${ICEDTEA_PREFIX}"

OPENJDK_CHANGESET = "22cc03983e20"
OPENJDK_FILE = "${OPENJDK_CHANGESET}.tar.bz2"
OPENJDK_URI = "${ICEDTEA_HG_URL}/archive/${OPENJDK_FILE};name=openjdk;unpack=false"
SRC_URI[openjdk.md5sum] = "f98b0f7a69f9427a5b3775dddddc89cb"
SRC_URI[openjdk.sha256sum] = "758227833982371e3a94def84226a947f8dbbd176517f313b8cb96840bdea41e"

HOTSPOT_CHANGESET = "0e651e004747"
HOTSPOT_FILE = "${HOTSPOT_CHANGESET}.tar.gz"
HOTSPOT_URI = "${ICEDTEA_HG_URL}/hotspot/archive/${HOTSPOT_FILE};name=hotspot;unpack=false"
SRC_URI[hotspot.md5sum] = "edd627c8781161eb33006ed668d833e0"
SRC_URI[hotspot.sha256sum] = "d68455e5cdb14280cd61155a4e9d531e90b073607f4367e93ead0fcf34476ae1"

CORBA_CHANGESET = "5617f6c5cc94"
CORBA_FILE = "${CORBA_CHANGESET}.tar.gz"
CORBA_URI = "${ICEDTEA_HG_URL}/corba/archive/${CORBA_FILE};name=corba;unpack=false"
SRC_URI[corba.md5sum] = "920f1a788a7fdef29a5cd70892331251"
SRC_URI[corba.sha256sum] = "963915483530f311ff313635f79ed11ea7ce5a1c0dbee5d1acb1994132857fa3"

JAXP_CHANGESET = "1cf75c0e2c96"
JAXP_FILE = "${JAXP_CHANGESET}.tar.gz"
JAXP_URI = "${ICEDTEA_HG_URL}/jaxp/archive/${JAXP_FILE};name=jaxp;unpack=false"
SRC_URI[jaxp.md5sum] = "56e609548b322149cb84604f232a4602"
SRC_URI[jaxp.sha256sum] = "8ce48c704f38285207ee6dc56c45b2d214083b4d4d36be02901401b594ce701e"

JAXWS_CHANGESET = "7edfbfe974f2"
JAXWS_FILE = "${JAXWS_CHANGESET}.tar.gz"
JAXWS_URI = "${ICEDTEA_HG_URL}/jaxws/archive/${JAXWS_FILE};name=jaxws;unpack=false"
SRC_URI[jaxws.md5sum] = "2deecec809ea8e38835678889c2bc3ac"
SRC_URI[jaxws.sha256sum] = "823ca6b8fd780bf1b1565a90cfc8ec6f0ee422a5d25ffb20b1ce0272dc4955aa"

JDK_CHANGESET = "50f6f276a06c"
JDK_FILE = "${JDK_CHANGESET}.tar.gz"
JDK_URI = "${ICEDTEA_HG_URL}/jdk/archive/${JDK_FILE};name=jdk;unpack=false"
SRC_URI[jdk.md5sum] = "7ee77eeeff600c5a4763b4ac76fd62bc"
SRC_URI[jdk.sha256sum] = "5f8b5edbebb358730425e64a31eaa11c346467ba10ffe1848f2d2ad2ea53bc3d"

LANGTOOLS_CHANGESET = "b534c4c6cd9b"
LANGTOOLS_FILE = "${LANGTOOLS_CHANGESET}.tar.gz"
LANGTOOLS_URI = "${ICEDTEA_HG_URL}/langtools/archive/${LANGTOOLS_FILE};name=langtools;unpack=false"
SRC_URI[langtools.md5sum] = "16b72f3fea8ac4e5b50de693e87f9c53"
SRC_URI[langtools.sha256sum] = "c77dd42d83f06d18fa8aa65c93d137608a2e02cf24b68fc10d7b1c0bcc12a93c"

CACAO_VERSION = "a567bcb7f589"
CACAO_FILE = "${CACAO_VERSION}.tar.gz"
CACAO_URI = "http://icedtea.classpath.org/download/drops/cacao/${CACAO_FILE};name=cacao;unpack=false"
SRC_URI[cacao.md5sum] = "ec1def7f0d3d25e9e7da47c480f26a73"
SRC_URI[cacao.sha256sum] = "d49f79debc131a5694cae6ab3ba2864e7f3249ee8d9dc09aae8afdd4dc6b09f9"

JAMVM_VERSION = "4617da717ecb05654ea5bb9572338061106a414d"
JAMVM_FILE = "jamvm-${JAMVM_VERSION}.tar.gz"
JAMVM_URI = "http://icedtea.classpath.org/download/drops/jamvm/${JAMVM_FILE};name=jamvm;unpack=false"
SRC_URI[jamvm.md5sum] = "740c2587502831cac6797d1233a7e27b"
SRC_URI[jamvm.sha256sum] = "47fce7bd556c1b1d29a93b8c45497e0d872b48b7f535066b303336f29d0f0d8d"

# Allow overriding this separately
OEPATCHES = "\
	file://build-hacks.patch \
	file://cacao-libtoolize.patch \
	file://cacao-loadavg-makefile.patch \
	file://fix_hotspot_crosscompile.patch \
	file://fix-checksums.patch \
	file://jamvm-extract.patch \
	file://cacao-loadavg.patch;apply=no \
        file://cacao-arm-ucontext.patch;apply=no \
	"

# Allow overriding this separately
ICEDTEAPATCHES = "\
	file://icedtea-crosscompile-fix.patch;apply=no \
	file://icedtea-hostbuildcc.patch;apply=no \
	file://icedtea-unbreak-float.patch;apply=no \
	file://icedtea-remove_werror.patch;apply=no \
        file://icedtea-libnet-renaming.patch;apply=no \
	file://icedtea-fix-xrender.patch;apply=no \
	file://icedtea-shark-arm-linux-cpu-detection.patch;apply=no \
	file://icedtea-corba-parallel-make.patch;apply=no \
        file://icedtea-zero-hotspotfix.patch;apply=no \
	"
ICEDTEAPATCHES_append_powerpc = " \
	file://icedtea-jdk-nio-use-host-cc.patch;apply=no \
	file://icedtea-jdk-ppc64-jvm-cfg.patch;apply=no \
	file://icedtea-jdk-powerpc-atomic64.patch;apply=no \
        "
ICEDTEAPATCHES_append_powerpc64 = " \
	file://icedtea-jdk-nio-use-host-cc.patch;apply=no \
	file://icedtea-jdk-ppc64-jvm-cfg.patch;apply=no \
        "
ICEDTEAPATCHES_append_libc-uclibc = " \
        file://icedtea-hotspot-isfinte.patch;apply=no \
        file://icedtea-hotspot-glibc-version.patch;apply=no \
        file://icedtea-hotspot-loadavg.patch;apply=no \
        file://icedtea-hotspot-isnanf.patch;apply=no \
        file://icedtea-jdk-iconv-uclibc.patch;apply=no \
        file://icedtea-jdk-remove-unused-backtrace.patch;apply=no \
        file://icedtea-jdk-unpack-uclibc.patch;apply=no \
	file://icedtea-hotspot-dlvsym-uclibc.patch;apply=no \
        "

# Allow overriding this separately
DISTRIBUTION_PATCHES = "\
	patches/icedtea-crosscompile-fix.patch \
	patches/icedtea-hostbuildcc.patch \
	patches/icedtea-unbreak-float.patch \
	patches/icedtea-remove_werror.patch \
        patches/icedtea-libnet-renaming.patch \
	patches/icedtea-fix-xrender.patch \
	patches/icedtea-shark-arm-linux-cpu-detection.patch \
	patches/icedtea-corba-parallel-make.patch \
        patches/icedtea-zero-hotspotfix.patch \
	"

DISTRIBUTION_PATCHES_append_libc-uclibc = "\
        patches/icedtea-hotspot-isfinte.patch \
        patches/icedtea-hotspot-isnanf.patch \
        patches/icedtea-hotspot-glibc-version.patch \
        patches/icedtea-hotspot-loadavg.patch \
        patches/icedtea-jdk-iconv-uclibc.patch \
        patches/icedtea-jdk-remove-unused-backtrace.patch \
        patches/icedtea-jdk-unpack-uclibc.patch \
	patches/icedtea-hotspot-dlvsym-uclibc.patch \
        "

DISTRIBUTION_PATCHES_append_powerpc = " \
	patches/icedtea-jdk-nio-use-host-cc.patch \
	patches/icedtea-jdk-ppc64-jvm-cfg.patch \
	patches/icedtea-jdk-powerpc-atomic64.patch \
        "
DISTRIBUTION_PATCHES_append_powerpc64 = " \
	patches/icedtea-jdk-nio-use-host-cc.patch \
	patches/icedtea-jdk-ppc64-jvm-cfg.patch \
        "
export DISTRIBUTION_PATCHES
