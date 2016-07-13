PATCHES_URI="\
    file://remove-shell-variables-from-autoheader.patch;striplevel=0 \
    file://filter-aclocal-copy-too.patch;striplevel=0 \
    file://dont-expect-fqpn-for-make.patch;striplevel=0 \
    file://openjdk8-no-genx11-in-headless.patch;apply=no \
    file://openjdk8-no-unused-deps.patch;apply=no \
    file://openjdk8-avoid-early-ldflags-expansion.patch;apply=no \
    file://openjdk8-find-compiler-fix-env-respect.patch;apply=no \
    file://openjdk8-prevent-debuginfo-in-favour-of-openembedded-package-split.patch;apply=no \
"

# Name of the directory containing the compiled output
BUILD_DIR = "openjdk.build"
BUILD_DIR_ECJ = "openjdk.build-ecj"

# Force arm mode for now
ARM_INSTRUCTION_SET_armv4t = "ARM"

# Enable zero mode for arm based builds, as normal hotspot fails to build 
PACKAGECONFIG_append_arm = " zero"

CORBA_CHANGESET = "7deeb4f70404"
SRC_URI[corba.md5sum] = "544b4963d14fb7155b12dbc56d058649"
SRC_URI[corba.sha256sum] = "a75c31706f634585baf0d0a0b20e321ac634d41d6afb62bd6ffb1f9c0b766d09"

HOTSPOT_CHANGESET = "d7b01fb81aa8"
SRC_URI[hotspot.md5sum] = "9a94802c1179faedf06d65d2f6fcc6c7"
SRC_URI[hotspot.sha256sum] = "5dacf0b9c86aa78061ca87c9ade1708b56deba35e2e559dcf9dbc50d85ba3ace"

JAXP_CHANGESET = "acbcb6682c9b"
SRC_URI[jaxp.md5sum] = "34b6700d03a0e2f13a272b4121536544"
SRC_URI[jaxp.sha256sum] = "b6b60e174c3d980773dd56e0a2e7cacc26b05e401f6a08a1ffef594b6166865a"

JAXWS_CHANGESET = "6aba0f814a15"
SRC_URI[jaxws.md5sum] = "bad8a6e540dca0889d5c0edef47fe6ca"
SRC_URI[jaxws.sha256sum] = "ae57bb090ec2c5338c6f740dbfd20a92f52e60379b764c4bc874464c5955b375"

JDK_CHANGESET = "39baa472e20c"
SRC_URI[jdk.md5sum] = "746e4d38fa3d31a22239d160688ed447"
SRC_URI[jdk.sha256sum] = "e3587fa57eec72c561f0695723649a745966bb2a74803ff8a451b80fd2079f99"

LANGTOOLS_CHANGESET = "10ffafaf5340"
SRC_URI[langtools.md5sum] = "4562acae958cc9b9f68300d5c2e6feb3"
SRC_URI[langtools.sha256sum] = "5d14b666fbc6ee93d60c6a135eb8163a95ca5de96d390894e0c0b59719cf7fe4"

NASHORN_CHANGESET = "9ff5c2181333"
SRC_URI[nashorn.md5sum] = "c6d234d73ab4d95072b7600b731bbfff"
SRC_URI[nashorn.sha256sum] = "f56ee0bc65c8f4954bbec0e777c0158a44dc4b744407991a96f6627be433807d"

OPENJDK_CHANGESET = "e8bed1496ff2"
SRC_URI[openjdk.md5sum] = "182992a90cbe209b34142f934319704b"
SRC_URI[openjdk.sha256sum] = "d835a9adcf766e68d5a73fb36040d9e35b36c0363c883b8f05560c49bb22bf0c"

OPENJDK_HG_U = "jdk8u"
OPENJDK_HG_URL = "http://hg.openjdk.java.net/jdk8u/${OPENJDK_HG_U}"

OPENJDK_FILE = "${OPENJDK_CHANGESET}.tar.bz2"
OPENJDK_URI = "${OPENJDK_HG_URL}/archive/${OPENJDK_FILE};name=openjdk"

HOTSPOT_FILE = "${HOTSPOT_CHANGESET}.tar.bz2"
HOTSPOT_URI = "${OPENJDK_HG_URL}/hotspot/archive/${HOTSPOT_FILE};name=hotspot;unpack=false"

CORBA_FILE = "${CORBA_CHANGESET}.tar.bz2"
CORBA_URI = "${OPENJDK_HG_URL}/corba/archive/${CORBA_FILE};name=corba;unpack=false"

JAXP_FILE = "${JAXP_CHANGESET}.tar.bz2"
JAXP_URI = "${OPENJDK_HG_URL}/jaxp/archive/${JAXP_FILE};name=jaxp;unpack=false"

JAXWS_FILE = "${JAXWS_CHANGESET}.tar.bz2"
JAXWS_URI = "${OPENJDK_HG_URL}/jaxws/archive/${JAXWS_FILE};name=jaxws;unpack=false"

JDK_FILE = "${JDK_CHANGESET}.tar.bz2"
JDK_URI = "${OPENJDK_HG_URL}/jdk/archive/${JDK_FILE};name=jdk;unpack=false"

LANGTOOLS_FILE = "${LANGTOOLS_CHANGESET}.tar.bz2"
LANGTOOLS_URI = "${OPENJDK_HG_URL}/langtools/archive/${LANGTOOLS_FILE};name=langtools;unpack=false"

NASHORN_FILE = "${NASHORN_CHANGESET}.tar.bz2"
NASHORN_URI = "${OPENJDK_HG_URL}/nashorn/archive/${NASHORN_FILE};name=nashorn;unpack=false"
#
#CACAO_VERSION = "e215e36be9fc"
#CACAO_FILE = "${CACAO_VERSION}.tar.gz"
#CACAO_URI = "http://icedtea.wildebeest.org/download/drops/cacao/${CACAO_FILE};name=cacao;unpack=false"
#SRC_URI[cacao.md5sum] = "79f95f0aea4ba04cf2f1a8632ac66d14"
#SRC_URI[cacao.sha256sum] = "4966514c72ee7ed108b882d9b6e65c3adf8a8f9c2dccb029f971b3c8cb4870ab"
#
#JAMVM_VERSION = "ec18fb9e49e62dce16c5094ef1527eed619463aa"
#JAMVM_FILE = "jamvm-${JAMVM_VERSION}.tar.gz"
#JAMVM_URI = "http://icedtea.wildebeest.org/download/drops/jamvm/${JAMVM_FILE};name=jamvm;unpack=false"
#SRC_URI[jamvm.md5sum] = "d50ae193d01a9251e10679c7a2cc6ff1"
#SRC_URI[jamvm.sha256sum] = "31810266666c23822942aac62a78019c2c4589e1c5ee48329cbf42652d4437bc"
