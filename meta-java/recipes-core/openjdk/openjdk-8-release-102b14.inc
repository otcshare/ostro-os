PATCHES_URI="\
    file://remove-shell-variables-from-autoheader.patch;striplevel=0 \
    file://filter-aclocal-copy-too.patch;striplevel=0 \
    file://dont-expect-fqpn-for-make.patch;striplevel=0 \
    file://openjdk8-no-genx11-in-headless.patch;apply=no \
    file://openjdk8-no-unused-deps.patch;apply=no \
    file://openjdk8-find-compiler-fix-env-respect.patch;apply=no \
    file://openjdk8-prevent-debuginfo-in-favour-of-openembedded-package-split.patch;apply=no \
"

# Name of the directory containing the compiled output
BUILD_DIR = "openjdk.build"
BUILD_DIR_ECJ = "openjdk.build-ecj"

# Force arm mode for now
ARM_INSTRUCTION_SET_armv4t = "ARM"

# readdir_r was deprecated in glibc-2.24. Ignore the error for now
# NOTE: When updating the recipe, please check if this is still needed
CFLAGS_append = " -Wno-error=deprecated-declarations"

# Enable zero mode for arm based builds, as normal hotspot fails to build
PACKAGECONFIG_append_arm = " zero"

CORBA_CHANGESET = "56b133772ec1"
SRC_URI[corba.md5sum] = "b67bd442400e6805ddb986e78adc2834"
SRC_URI[corba.sha256sum] = "d5aabb9b3681b0593dde1b9eee4ff9b4cbabe7568b041f9e63e6fa73ba11bb86"

HOTSPOT_CHANGESET = "ac29c9c1193a"
SRC_URI[hotspot.md5sum] = "4383d833de07fc617595a01a78efd0fc"
SRC_URI[hotspot.sha256sum] = "1e36c6d207ac1a7d6d08f28a61bf061188df0562d89baf606138d8245d690982"

JAXP_CHANGESET = "1f032000ff4b"
SRC_URI[jaxp.md5sum] = "a4a46860d00f8b513a690166b9ae0b56"
SRC_URI[jaxp.sha256sum] = "dfa0098ca9b9f99cb9de4ee9f3c61b0ad28f968ecda770f09e603c6dd8f78df3"

JAXWS_CHANGESET = "81f2d81a48d7"
SRC_URI[jaxws.md5sum] = "0077cb7f1d1b31ba882f910bd3c30050"
SRC_URI[jaxws.sha256sum] = "c28322d7a9805d06b6f3a49d316aa4746076dfc106431a952fe0d12b6690cbdc"

JDK_CHANGESET = "48c99b423839"
SRC_URI[jdk.md5sum] = "316fc871a823ff8f1db39a2fca51bd12"
SRC_URI[jdk.sha256sum] = "bca18458ba0a0b8d79639829b8a71cdf65dd788b5c28658102b6b4691a47a420"

LANGTOOLS_CHANGESET = "0549bf2f507d"
SRC_URI[langtools.md5sum] = "bff92b915d26afd0c9b7c4b9013ee424"
SRC_URI[langtools.sha256sum] = "4a918bab7a8f13b6705085be0d043b03e24afb4ff3c67ad98000c6b9fe577cb8"

NASHORN_CHANGESET = "0948e61a3722"
SRC_URI[nashorn.md5sum] = "19e79a31ad20b55b47d6b9f1b20eaac0"
SRC_URI[nashorn.sha256sum] = "caa1f648cfbe45c081460bc9c2d9a7b83910bb468c325d8acc2ee4417460915e"

OPENJDK_CHANGESET = "bf0932d3e0f8"
SRC_URI[openjdk.md5sum] = "2b52cc3d439fe0da2ecbb28671fbe5aa"
SRC_URI[openjdk.sha256sum] = "66fa6ecf3047b7d8a216c1372616babe96f0fb40e89cb51575b80bf602d9ba59"

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
