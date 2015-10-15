require icedtea7-native.inc

LIC_FILES_CHKSUM = "file://COPYING;md5=59530bdf33659b29e73d4adb9f9f6552"

FILESPATH =. "${FILE_DIRNAME}/openjdk-7-03b147:"

# Force arm mode for now
ARM_INSTRUCTION_SET_armv4t = "ARM"

ICEDTEA_URI = "http://icedtea.wildebeest.org/download/source/${ICEDTEA}.tar.gz;name=iced"

ICEDTEA_PREFIX = "icedtea7-forest-2.1"
ICEDTEA_HG_URL = "http://icedtea.classpath.org/hg/release/${ICEDTEA_PREFIX}"

OPENJDK_CHANGESET = "22cc03983e20"
OPENJDK_FILE = "${OPENJDK_CHANGESET}.tar.bz2"
OPENJDK_URI = "${ICEDTEA_HG_URL}/archive/${OPENJDK_FILE};name=openjdk;unpack=false"
SRC_URI[openjdk.md5sum] = "f98b0f7a69f9427a5b3775dddddc89cb"
SRC_URI[openjdk.sha256sum] = "758227833982371e3a94def84226a947f8dbbd176517f313b8cb96840bdea41e"

HOTSPOT_CHANGESET = "8b7c4c5f6ba9"
HOTSPOT_FILE = "${HOTSPOT_CHANGESET}.tar.gz"
HOTSPOT_URI = "${ICEDTEA_HG_URL}/hotspot/archive/${HOTSPOT_FILE};name=hotspot;unpack=false"
SRC_URI[hotspot.md5sum] = "cb45a8f19d77acc1f4f48e75e36a27fe"
SRC_URI[hotspot.sha256sum] = "22866990d143e76ced94b76defa3051e5e5d9a51fd272d63daa0df272d6406a2"

CORBA_CHANGESET = "5617f6c5cc94"
CORBA_FILE = "${CORBA_CHANGESET}.tar.gz"
CORBA_URI = "${ICEDTEA_HG_URL}/corba/archive/${CORBA_FILE};name=corba;unpack=false"
SRC_URI[corba.md5sum] = "920f1a788a7fdef29a5cd70892331251"
SRC_URI[corba.sha256sum] = "963915483530f311ff313635f79ed11ea7ce5a1c0dbee5d1acb1994132857fa3"

JAXP_CHANGESET = "7a8825b15df6"
JAXP_FILE = "${JAXP_CHANGESET}.tar.gz"
JAXP_URI = "${ICEDTEA_HG_URL}/jaxp/archive/${JAXP_FILE};name=jaxp;unpack=false"
SRC_URI[jaxp.md5sum] = "a0982b6df79739127871e355a40ca5a6"
SRC_URI[jaxp.sha256sum] = "297c8dbeed5afa5395b6be06b17282d53f8a888c2909074dfc1605afc0daf1c2"

JAXWS_CHANGESET = "7edfbfe974f2"
JAXWS_FILE = "${JAXWS_CHANGESET}.tar.gz"
JAXWS_URI = "${ICEDTEA_HG_URL}/jaxws/archive/${JAXWS_FILE};name=jaxws;unpack=false"
SRC_URI[jaxws.md5sum] = "2deecec809ea8e38835678889c2bc3ac"
SRC_URI[jaxws.sha256sum] = "823ca6b8fd780bf1b1565a90cfc8ec6f0ee422a5d25ffb20b1ce0272dc4955aa"

JDK_CHANGESET = "d5ddeffc4651"
JDK_FILE = "${JDK_CHANGESET}.tar.gz"
JDK_URI = "${ICEDTEA_HG_URL}/jdk/archive/${JDK_FILE};name=jdk;unpack=false"
SRC_URI[jdk.md5sum] = "27c28d6be213df818490e69f12efe475"
SRC_URI[jdk.sha256sum] = "e83e6234842376147a4c32451f23d629ba107e908ebdb0f367657f9cc6c1be98"

LANGTOOLS_CHANGESET = "b534c4c6cd9b"
LANGTOOLS_FILE = "${LANGTOOLS_CHANGESET}.tar.gz"
LANGTOOLS_URI = "${ICEDTEA_HG_URL}/langtools/archive/${LANGTOOLS_FILE};name=langtools;unpack=false"
SRC_URI[langtools.md5sum] = "16b72f3fea8ac4e5b50de693e87f9c53"
SRC_URI[langtools.sha256sum] = "c77dd42d83f06d18fa8aa65c93d137608a2e02cf24b68fc10d7b1c0bcc12a93c"

CACAO_VERSION = "a567bcb7f589"
CACAO_FILE = "${CACAO_VERSION}.tar.gz"
CACAO_URI = "http://icedtea.wildebeest.org/download/drops/cacao/${CACAO_FILE};name=cacao;unpack=false"
SRC_URI[cacao.md5sum] = "ec1def7f0d3d25e9e7da47c480f26a73"
SRC_URI[cacao.sha256sum] = "d49f79debc131a5694cae6ab3ba2864e7f3249ee8d9dc09aae8afdd4dc6b09f9"

JAMVM_VERSION = "4617da717ecb05654ea5bb9572338061106a414d"
JAMVM_FILE = "jamvm-${JAMVM_VERSION}.tar.gz"
JAMVM_URI = "http://icedtea.wildebeest.org/download/drops/jamvm/${JAMVM_FILE};name=jamvm;unpack=false"
SRC_URI[jamvm.md5sum] = "740c2587502831cac6797d1233a7e27b"
SRC_URI[jamvm.sha256sum] = "47fce7bd556c1b1d29a93b8c45497e0d872b48b7f535066b303336f29d0f0d8d"

ICEDTEA_PATCHES = " \
        file://disable-library-checks.patch \
        file://build-hacks-native.patch \
        file://icedtea-sane-x86-arch-name.patch \
	file://fix-checksums.patch \
        "

OPENJDK_PATCHES = " \
        file://icedtea-ecj-disable-compilation.patch;apply=no \
	file://icedtea-unbreak-float.patch;apply=no \
	file://icedtea-corba-parallel-make.patch;apply=no \
        file://icedtea-hotspot-make-arch-sane-for-x86.patch;apply=no \
        file://icedtea-jdk-sane-x86-arch.patch;apply=no \
	file://icedtea-flags.patch;apply=no \
	file://icedtea-openjdk-remove-currency-data-generation-expi.patch;apply=no \
	file://icedtea-change-to-gdb-debug-format.patch;apply=no \
	file://icedtea-disable-x11-in-headless.patch;apply=no \
	file://icedtea-disable-sun.applet-for-tools-in-headless.patch;apply=no \
        "

OPENJDK_HEADLESS_PATCHES = " \
	patches/icedtea-disable-x11-in-headless.patch \
	patches/icedtea-disable-sun.applet-for-tools-in-headless.patch \
	"

CLEAN_X11_DISTRIBUTION_PATCH = "${@base_contains('PACKAGECONFIG', 'x11', '', '${OPENJDK_HEADLESS_PATCHES}', d)}"

export DISTRIBUTION_PATCHES = " \
        patches/icedtea-ecj-disable-compilation.patch \
	patches/icedtea-unbreak-float.patch \
	patches/icedtea-corba-parallel-make.patch \
        patches/icedtea-hotspot-make-arch-sane-for-x86.patch \
        patches/icedtea-jdk-sane-x86-arch.patch \
	patches/icedtea-flags.patch \
	patches/icedtea-openjdk-remove-currency-data-generation-expi.patch \
	patches/icedtea-change-to-gdb-debug-format.patch \
	${CLEAN_X11_DISTRIBUTION_PATCH} \
        "
