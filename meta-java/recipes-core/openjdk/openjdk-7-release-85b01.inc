require openjdk-7-common.inc

LIC_FILES_CHKSUM = "file://COPYING;md5=59530bdf33659b29e73d4adb9f9f6552"

FILESPATH =. "${FILE_DIRNAME}/openjdk-7-85b01:"

# Name of the directory containing the compiled output
BUILD_DIR = "openjdk.build"
BUILD_DIR_ECJ = "openjdk.build-ecj"

# Force arm mode for now
ARM_INSTRUCTION_SET_armv4t = "ARM"

ICEDTEA_URI = "http://icedtea.wildebeest.org/download/source/${ICEDTEA}.tar.gz;name=iced"

ICEDTEA_PREFIX = "icedtea7-forest-2.6"
ICEDTEA_HG_URL = "http://icedtea.classpath.org/hg/release/${ICEDTEA_PREFIX}"

OPENJDK_FILE = "${OPENJDK_CHANGESET}.tar.bz2"
OPENJDK_URI = "${ICEDTEA_HG_URL}/archive/${OPENJDK_FILE};name=openjdk;unpack=false"

HOTSPOT_FILE = "${HOTSPOT_CHANGESET}.tar.bz2"
#HOTSPOT_URI = "${ICEDTEA_HG_URL}/hotspot/archive/${HOTSPOT_FILE};name=hotspot;unpack=false"
HOTSPOT_URI = "http://icedtea.classpath.org/hg/icedtea7-forest/hotspot/archive/${HOTSPOT_FILE};name=hotspot;unpack=false"

CORBA_FILE = "${CORBA_CHANGESET}.tar.bz2"
CORBA_URI = "${ICEDTEA_HG_URL}/corba/archive/${CORBA_FILE};name=corba;unpack=false"

JAXP_FILE = "${JAXP_CHANGESET}.tar.bz2"
JAXP_URI = "${ICEDTEA_HG_URL}/jaxp/archive/${JAXP_FILE};name=jaxp;unpack=false"

JAXWS_FILE = "${JAXWS_CHANGESET}.tar.bz2"
JAXWS_URI = "${ICEDTEA_HG_URL}/jaxws/archive/${JAXWS_FILE};name=jaxws;unpack=false"

JDK_FILE = "${JDK_CHANGESET}.tar.bz2"
JDK_URI = "${ICEDTEA_HG_URL}/jdk/archive/${JDK_FILE};name=jdk;unpack=false"

LANGTOOLS_FILE = "${LANGTOOLS_CHANGESET}.tar.bz2"
LANGTOOLS_URI = "${ICEDTEA_HG_URL}/langtools/archive/${LANGTOOLS_FILE};name=langtools;unpack=false"

CACAO_VERSION = "c182f119eaad"
CACAO_FILE = "cacao-${CACAO_VERSION}.tar.gz"
CACAO_URI = "http://icedtea.classpath.org/download/drops/cacao/${CACAO_FILE};name=cacao;unpack=false"
SRC_URI[cacao.md5sum] = "df428cf98e5baf28c1d186bc9b92fb01"
SRC_URI[cacao.sha256sum] = "eade43f6c5da8b3b5a64e6b206b624eaca88539f80101d7164d6aa426eb590b1"

JAMVM_VERSION = "ec18fb9e49e62dce16c5094ef1527eed619463aa"
JAMVM_FILE = "jamvm-${JAMVM_VERSION}.tar.gz"
JAMVM_URI = "http://icedtea.wildebeest.org/download/drops/jamvm/${JAMVM_FILE};name=jamvm;unpack=false"
SRC_URI[jamvm.md5sum] = "d50ae193d01a9251e10679c7a2cc6ff1"
SRC_URI[jamvm.sha256sum] = "31810266666c23822942aac62a78019c2c4589e1c5ee48329cbf42652d4437bc"

# Split up patches to allow overriding them separately
OEPATCHES = "\
	file://build-hacks.patch \
	file://fix_hotspot_crosscompile.patch \
	"

ICEDTEAPATCHES = "\
	file://icedtea-zero-hotspotfix.patch;apply=no \
	file://icedtea-jdk-nio-use-host-cc.patch;apply=no \
	file://icedtea-jdk-build-nio-gensor-genuc-gensc-static.patch;apply=no \
	file://icedtea-jdk-rmi-crosscompile.patch;apply=no \
	file://icedtea-crosscompile-fix.patch;apply=no \
	file://icedtea-xawt-crosscompile-fix.patch;apply=no \
	"

DISTRIBUTION_PATCHES = "\
	patches/icedtea-zero-hotspotfix.patch \
	patches/icedtea-jdk-nio-use-host-cc.patch \
	patches/icedtea-jdk-build-nio-gensor-genuc-gensc-static.patch \
	patches/icedtea-jdk-rmi-crosscompile.patch \
	patches/icedtea-crosscompile-fix.patch \
	patches/icedtea-xawt-crosscompile-fix.patch \
	"

export DISTRIBUTION_PATCHES
