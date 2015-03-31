require openjdk-7-common.inc

LIC_FILES_CHKSUM = "file://COPYING;md5=59530bdf33659b29e73d4adb9f9f6552"

FILESPATH =. "${FILE_DIRNAME}/openjdk-7-25b30:"

# Name of the directory containing the compiled output
BUILD_DIR = "openjdk.build"
BUILD_DIR_ECJ = "openjdk.build-ecj"

# Force arm mode for now
ARM_INSTRUCTION_SET_armv4t = "ARM"

ICEDTEA_URI = "http://icedtea.wildebeest.org/download/source/${ICEDTEA}.tar.gz;name=iced"

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

CACAO_VERSION = "e215e36be9fc"
CACAO_FILE = "${CACAO_VERSION}.tar.gz"
CACAO_URI = "http://icedtea.wildebeest.org/download/drops/cacao/${CACAO_FILE};name=cacao;unpack=false"
SRC_URI[cacao.md5sum] = "79f95f0aea4ba04cf2f1a8632ac66d14"
SRC_URI[cacao.sha256sum] = "4966514c72ee7ed108b882d9b6e65c3adf8a8f9c2dccb029f971b3c8cb4870ab"

JAMVM_VERSION = "0972452d441544f7dd29c55d64f1ce3a5db90d82"
JAMVM_FILE = "jamvm-${JAMVM_VERSION}.tar.gz"
JAMVM_URI = "http://icedtea.wildebeest.org/download/drops/jamvm/${JAMVM_FILE};name=jamvm;unpack=false"
SRC_URI[jamvm.md5sum] = "f4616713ec609e35aa8070811bd952aa"
SRC_URI[jamvm.sha256sum] = "bfa706402ac934d24f7119eb78f6be65e91439a4b2e49dbcc21e288137808f03"

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
	file://icedtea-jdk-nio-use-host-cc.patch;apply=no \
        file://icedtea-unset-NIO_PLATFORM_CLASSES_ROOT_DIR.patch;apply=no \
        file://icedtea-openjdk-remove-currency-data-generation-expi.patch;apply=no \
        file://icedtea-add-usr-lib-jni-to-DEFAULT_LIBPATH.patch;apply=no \
	"
ICEDTEAPATCHES_append_powerpc = " \
	file://icedtea-jdk-ppc64-jvm-cfg.patch;apply=no \
	file://icedtea-jdk-powerpc-atomic64.patch;apply=no \
        "
ICEDTEAPATCHES_append_powerpc64 = " \
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
	patches/icedtea-jdk-nio-use-host-cc.patch \
	patches/icedtea-unset-NIO_PLATFORM_CLASSES_ROOT_DIR.patch \
	patches/icedtea-openjdk-remove-currency-data-generation-expi.patch \
	patches/icedtea-add-usr-lib-jni-to-DEFAULT_LIBPATH.patch \
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
	patches/icedtea-jdk-ppc64-jvm-cfg.patch \
	patches/icedtea-jdk-powerpc-atomic64.patch \
        "
DISTRIBUTION_PATCHES_append_powerpc64 = " \
	patches/icedtea-jdk-ppc64-jvm-cfg.patch \
        "
export DISTRIBUTION_PATCHES
