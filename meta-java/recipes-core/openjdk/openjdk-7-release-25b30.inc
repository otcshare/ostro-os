require openjdk-7-common.inc

LIC_FILES_CHKSUM = "file://COPYING;md5=59530bdf33659b29e73d4adb9f9f6552"

FILESPATH =. "${FILE_DIRNAME}/openjdk-7-25b30:"

# Name of the directory containing the compiled output
BUILD_DIR = "openjdk.build"
BUILD_DIR_ECJ = "openjdk.build-ecj"

# Force arm mode for now
ARM_INSTRUCTION_SET_armv4t = "ARM"

ICEDTEA_URI = "http://icedtea.classpath.org/download/source/${ICEDTEA}.tar.gz;name=iced"

ICEDTEA_PREFIX = "icedtea7-forest-2.3"
ICEDTEA_HG_URL = "http://icedtea.classpath.org/hg/release/${ICEDTEA_PREFIX}"

OPENJDK_FILE = "${OPENJDK_CHANGESET}.tar.bz2"
OPENJDK_URI = "${ICEDTEA_HG_URL}/archive/${OPENJDK_FILE};name=openjdk;unpack=false"

HOTSPOT_FILE = "${HOTSPOT_CHANGESET}.tar.gz"
HOTSPOT_URI = "${ICEDTEA_HG_URL}/hotspot/archive/${HOTSPOT_FILE};name=hotspot;unpack=false"

CORBA_FILE = "${CORBA_CHANGESET}.tar.gz"
CORBA_URI = "${ICEDTEA_HG_URL}/corba/archive/${CORBA_FILE};name=corba;unpack=false"

JAXP_FILE = "${JAXP_CHANGESET}.tar.gz"
JAXP_URI = "${ICEDTEA_HG_URL}/jaxp/archive/${JAXP_FILE};name=jaxp;unpack=false"

JAXWS_FILE = "${JAXWS_CHANGESET}.tar.gz"
JAXWS_URI = "${ICEDTEA_HG_URL}/jaxws/archive/${JAXWS_FILE};name=jaxws;unpack=false"

JDK_FILE = "${JDK_CHANGESET}.tar.gz"
JDK_URI = "${ICEDTEA_HG_URL}/jdk/archive/${JDK_FILE};name=jdk;unpack=false"

LANGTOOLS_FILE = "${LANGTOOLS_CHANGESET}.tar.gz"
LANGTOOLS_URI = "${ICEDTEA_HG_URL}/langtools/archive/${LANGTOOLS_FILE};name=langtools;unpack=false"

CACAO_VERSION = "a567bcb7f589"
CACAO_FILE = "${CACAO_VERSION}.tar.gz"
CACAO_URI = "http://icedtea.classpath.org/download/drops/cacao/${CACAO_FILE};name=cacao;unpack=false"
SRC_URI[cacao.md5sum] = "ec1def7f0d3d25e9e7da47c480f26a73"
SRC_URI[cacao.sha256sum] = "d49f79debc131a5694cae6ab3ba2864e7f3249ee8d9dc09aae8afdd4dc6b09f9"

JAMVM_VERSION = "0972452d441544f7dd29c55d64f1ce3a5db90d82"
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
        file://cacao-update.patch \
	file://cacao-loadavg.patch;apply=no \
        file://cacao-arm-ucontext.patch;apply=no \
        file://remove-sun.misc.Perf-debug-code.patch;apply=no \
        file://fix-checksums.patch \
	"

# overrride the jamvm patch for now, needs to be solved upstream
do_unpackpost() {
    cp ${WORKDIR}/remove-sun.misc.Perf-debug-code.patch ${S}/patches/jamvm
}

addtask unpackpost after do_unpack before do_patch

# Allow overriding this separately
ICEDTEAPATCHES = "\
	file://icedtea-crosscompile-fix.patch;apply=no \
	file://icedtea-unbreak-float.patch;apply=no \
	file://icedtea-remove_werror.patch;apply=no \
        file://icedtea-libnet-renaming.patch;apply=no \
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
	patches/icedtea-unbreak-float.patch \
	patches/icedtea-remove_werror.patch \
        patches/icedtea-libnet-renaming.patch \
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
