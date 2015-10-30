require openjdk-common.inc
ICEDTEA = "icedtea-${ICEDTEA_VERSION}"

INC_PR = "r6"

SRC_URI = " \
  ${ICEDTEA_URI} \
  ${OPENJDK_URI} \
  ${HOTSPOT_URI} \
  ${CORBA_URI} \
  ${JAXP_URI} \
  ${JAXWS_URI} \
  ${JDK_URI} \
  ${LANGTOOLS_URI} \
  ${OEPATCHES} \
  ${ICEDTEAPATCHES} \
  file://jvm.cfg \
  "

JDKPN = "openjdk-7"
JDK_DIR = "java-7-openjdk"

PN = "${JDKPN}-jre"
PROVIDES += "${JDKPN}"

DEPENDS = " \
           icedtea7-native zip-native ant-native \
           zlib libxslt-native \
	   jpeg libpng giflib \
           gtk+ glib-2.0 \
           cups fontconfig \
	   rhino krb5 \
	   libxt libxinerama libxrender libxtst libxi \
	   freetype alsa-lib libffi \
          "

# No package should directly depend on this (it should require
# java2-runtime instead).
PRIVATE_LIBS = "\
	lib.so libunpack.so libverify.so libjava.so libzip.so libnpt.so \
	libjava_crw_demo.so libhprof.so libjavanet.so libnio.so \
	libmanagement.so libinstrument.so libjsound.so libjsoundalsa.so \
	libj2pcsc.so libj2pkcs11.so libj2gss.so libmlib_image.so \
	libawt.so libsplashscreen.so libfreetype.so.6 libfontmanager.so \
	libjpeg.so liblcms.so librmi.so libjawt.so libjaas_unix.so \
	libattach.so libjdwp.so libdt_socket.so libhpi.so libjli.so \
	libmawt.so libjvm.so \
	libversionCheck.so libcompiledMethodLoad.so libgctest.so \
	libheapViewer.so libheapTracker.so libminst.so libmtrace.so \
	libwaiters.so libhprof.so \
       "

export ALT_CUPS_HEADERS_PATH = "${STAGING_INCDIR}"
export ALT_FREETYPE_HEADERS_PATH = "${STAGING_INCDIR}/freetype2"
export ALT_FREETYPE_LIB_PATH = "${STAGING_LIBDIR}"
export CACAO_CONFIGURE_ARGS = " \
	${@['','--enable-softfloat'][bb.data.getVar('TARGET_FPU',d,1) == 'soft']}"

JAVA_HOME[unexport] = "1"

# OpenJDK supports parallel compilation but uses a plain number for this.
# In OE we have PARALLEL_MAKE which is the actual option passed to make,
# e.g. "-j 4".

OPENJDK_PARALLEL_MAKE := "${PARALLEL_MAKE}"
PARALLEL_MAKE =  ""

def get_jdk7_jobs(d):
    import bb

    pm = bb.data.getVar('OPENJDK_PARALLEL_MAKE', d, 1);
    if not pm:
        return "1"

    pm = pm.split("j");
    if (len(pm) == 2):
        return pm[1].strip()

    # Whatever found in PARALLEL_MAKE was not suitable.
    return "1"

JDK_JOBS = "${@get_jdk7_jobs(d)}"

EXTRA_OECONF = " \
        --disable-tests \
	--disable-hotspot-tests \
	--disable-langtools-tests \
	--disable-jdk-tests \
	--disable-docs \
	--disable-nss \
	--disable-system-lcms \
	--disable-bootstrap \
	\
        --enable-zero \
	\
	--with-jdk-home=${STAGING_LIBDIR_JVM_NATIVE}/icedtea7-native \
	--with-rhino=${STAGING_DATADIR_JAVA}/rhino.jar \
	\
        --with-openjdk-src-zip=${WORKDIR}/${OPENJDK_FILE} \
	--with-hotspot-src-zip=${WORKDIR}/${HOTSPOT_FILE} \
	--with-corba-src-zip=${WORKDIR}/${CORBA_FILE} \
	--with-jaxp-src-zip=${WORKDIR}/${JAXP_FILE} \
	--with-jaxws-src-zip=${WORKDIR}/${JAXWS_FILE} \
	--with-jdk-src-zip=${WORKDIR}/${JDK_FILE} \
	--with-langtools-src-zip=${WORKDIR}/${LANGTOOLS_FILE} \
	\
	--with-parallel-jobs=${JDK_JOBS} \
	\
	--with-pkgversion=${PV} \
	--with-cc-for-build=${BUILD_CC} \
       "

# PCSC default value was changed to true and SCTP was added during the 2.6.0
# release so we disable them both explicitely here
EXTRA_OECONF += " \
	--disable-system-pcsc \
	--disable-system-sctp \
	"

do_configure_prepend() {
  echo "Configure with parallel-jobs: ${JDK_JOBS}"

  # Automatically copy everything that starts with "icedtea" (or "cacao") and ends with
  # ".patch" into the patches directory.
  find ${WORKDIR} -maxdepth 1 -name "icedtea*.patch" -exec cp {} ${S}/patches \;
  find ${WORKDIR} -maxdepth 1 -name "cacao*.patch" -exec cp {} ${S}/patches \;
}

do_configure_append() {
	oe_runmake patch
}

# Work around broken variable quoting in oe-stable 2009 and provide the variable
# via the environment which then overrides the erroneous value that was written
# into '${ICETDEA}/Makefile'.
# Icedtea's makefile is not compatible to parallelization so we cannot allow
# passing a valid ${PARALLEL_MAKE} to it. OTOH OpenJDK's makefiles are
# parallelizable and we need ${PARALLEL_MAKE} to derive the proper value.
# The base for this quirk is that GNU Make only considers the last "-j" option.
EXTRA_OEMAKE += 'CC="${CC}" CCC="${CXX}" CPP="${CPP}" CXX="${CXX}" CC_FOR_BUILD="${BUILD_CC}"'

EXTRA_OEMAKE += ' \
                OE_CFLAGS="${TARGET_CFLAGS}" \
                OE_CPPFLAGS="${TARGET_CPPFLAGS}" \
                OE_CXXFLAGS="${TARGET_CXXFLAGS}" \
                OE_LDFLAGS="${TARGET_LDFLAGS}" \
                ZIPEXE="${STAGING_BINDIR_NATIVE}/zip" \
		CROSS_COMPILE_ARCH="${JDK_ARCH}" \
		REQUIRED_ALSA_VERSION="" \
		DISABLE_HOTSPOT_OS_VERSION_CHECK=ok \
               '

# Provides the target architecture to the configure script.
export LLVM_CONFIGURE_ARCH="${@get_llvm_configure_arch(d)}"

OE_LAUNCHER_LDFLAGS = "-Wl,-rpath-link,${STAGING_LIBDIR}/llvm${WANT_LLVM_RELEASE} -Wl,-rpath,${libdir}/llvm${WANT_LLVM_RELEASE}"

OE_LAUNCHER_LDFLAGS_arm = ""

EXTRA_OEMAKE += 'OE_LAUNCHER_LDFLAGS="${OE_LAUNCHER_LDFLAGS}"'

do_compile() {

	bbnote "3/3 Building final JDK"

	# Build the final Hotspot + OpenJDK
	oe_runmake icedtea-stage2
}

do_install() {
	install -d ${D}${libdir_jvm}
	cp -R ${B}/${BUILD_DIR}/j2sdk-image ${D}${JDK_HOME}

	chmod u+rw -R ${D}${JDK_HOME}

	# Fix symlink which would point into staging in the binary package.
	ln -sf ${datadir_java}/rhino.jar ${D}${JDK_HOME}/jre/lib/rhino.jar

	# JRE is a subset of JDK. So to save space and resemble what the BIG distros
	# do we create symlinks from the JDK binaries to their counterparts in the
	# JRE folder (which have to exist by that time b/c of dependencies).
	for F in `find ${D}${JDK_HOME}/jre/bin -type f`
	do
		bf=`basename $F`
		bbnote "replace:" $bf
		rm ${D}${JDK_HOME}/bin/$bf
		ln -s ${JDK_HOME}/jre/bin/$bf ${D}${JDK_HOME}/bin/$bf
	done

        install -m644 ${WORKDIR}/jvm.cfg  ${D}${JDK_HOME}/jre/lib/${JDK_ARCH}/
        # workaround for shared libarary searching
	ln -sf ${JDK_HOME}/jre/lib/${JDK_ARCH}/server/libjvm.so ${D}${JDK_HOME}/jre/lib/${JDK_ARCH}/
}

# Notes about the ideas behind packaging:
# 1) User should install openjdk-7-jre. This is a provider of 'java2-runtime'.
# 2) This lets package mgmt install: openjdk-7-java
# -> openjdk-7-vm-shark|openjdk-7-vm-zero|openjdk-7-vm-cacao -> openjdk-7-common
#
# With opkg the zero VM is chosen which is good b/c that is the best known (= compatible)
# runtime. Installing other runtimes side-by-side is possible. Through jvm.cfg the following
# order of precedence is enforced: zero, shark, cacao. User can chose a different runtime
# by adding '-shark' or '-cacao' to the Java command (or by deinstalling an otherwise preferred
# runtime)
# 3) All other packages, including -jdk, are optional and not needed for normal Java apps.
PACKAGES = " \
            ${JDKPN}-jre \
	    ${JDKPN}-jre-dbg \
            ${JDKPN}-dbg \
            ${JDKPN}-demo-dbg \
            ${JDKPN}-demo \
            ${JDKPN}-source \
            ${JDKPN}-doc \
            ${JDKPN}-jdk \
            ${JDKPN}-java \
            ${JDKPN}-vm-zero \
            ${JDKPN}-common \
           "

FILES_${JDKPN}-dbg = "\
	${JDK_HOME}/bin/.debug \
	${JDK_HOME}/lib/.debug \
	${JDK_HOME}/lib/${JDK_ARCH}/jli/.debug \
	${JDK_HOME}/jre/bin/.debug \
	${JDK_HOME}/jre/lib/.debug \
	${JDK_HOME}/jre/lib/${JDK_ARCH}/.debug \
	${JDK_HOME}/jre/lib/${JDK_ARCH}/jli/.debug \
	${JDK_HOME}/jre/lib/${JDK_ARCH}/native_threads/.debug \
	${JDK_HOME}/jre/lib/${JDK_ARCH}/server/.debug \
	${JDK_HOME}/jre/lib/${JDK_ARCH}/headless/.debug \
	${JDK_HOME}/jre/lib/${JDK_ARCH}/xawt/.debug \
	${JDK_HOME}/jre/lib/${JDK_ARCH}/client/.debug \
       "

FILES_${JDKPN}-demo = "${JDK_HOME}/demo ${JDK_HOME}/sample"
RDEPENDS_${JDKPN}-demo = "${JDKPN}-jre"
FILES_${JDKPN}-demo-dbg = "\
	${JDK_HOME}/demo/jvmti/gctest/lib/.debug \
	${JDK_HOME}/demo/jvmti/heapTracker/lib/.debug \
	${JDK_HOME}/demo/jvmti/heapViewer/lib/.debug \
	${JDK_HOME}/demo/jvmti/hprof/lib/.debug \
	${JDK_HOME}/demo/jvmti/minst/lib/.debug \
	${JDK_HOME}/demo/jvmti/mtrace/lib/.debug \
	${JDK_HOME}/demo/jvmti/versionCheck/lib/.debug \
	${JDK_HOME}/demo/jvmti/waiters/lib/.debug \
	${JDK_HOME}/demo/jvmti/compiledMethodLoad/lib/.debug \
       "

FILES_${JDKPN}-source = "${JDK_HOME}/src.zip"

FILES_${JDKPN}-java = "${JDK_HOME}/jre/bin/java"

FILES_${JDKPN}-vm-zero = "${JDK_HOME}/jre/lib/${JDK_ARCH}/server/"

FILES_${JDKPN}-common = "${JDK_HOME}/jre/ASSEMBLY_EXCEPTION \
                          ${JDK_HOME}/jre/THIRD_PARTY_README \
                          ${JDK_HOME}/jre/LICENSE \
                          ${JDK_HOME}/ASSEMBLY_EXCEPTION \
                          ${JDK_HOME}/THIRD_PARTY_README \
                          ${JDK_HOME}/LICENSE \
                          ${JDK_HOME}/release \
                          ${JDK_HOME}/jre/lib \
                         "

FILES_${PN}_append = " \
	${JDK_HOME}/jre/bin/keytool \
	${JDK_HOME}/jre/bin/orbd \
	${JDK_HOME}/jre/bin/pack200 \
	${JDK_HOME}/jre/bin/rmid \
	${JDK_HOME}/jre/bin/rmiregistry \
	${JDK_HOME}/jre/bin/servertool \
	${JDK_HOME}/jre/bin/tnameserv \
	${JDK_HOME}/jre/bin/unpack200 \
	${JDK_HOME}/jre/bin/policytool \
	${JDK_HOME}/jre/bin/javaws \
	"

RDEPENDS_${JDKPN}-common = "librhino-java"

RPROVIDES_${JDKPN}-vm-zero = "java2-vm"

# Even though a vm is a hard dependency it is set as RRECOMMENDS so a single vm can get uninstalled:
# root@beaglebone:~/java# opkg remove openjdk-7-vm-shark
# No packages removed.
# Collected errors:
#  * print_dependents_warning: Package openjdk-7-vm-shark is depended upon by packages:
#  * print_dependents_warning: 	openjdk-7-java
#  * print_dependents_warning: These might cease to work if package openjdk-7-vm-shark is removed.
RRECOMMENDS_${JDKPN}-java = "java2-vm"

# For some reason shark and cacao do not automatically depends on -common.
# So we add that manually.

# There is a symlink to a .so but this one is valid.
INSANE_SKIP_${JDKPN}-vm-zero = "dev-so"
INSANE_SKIP_${JDKPN}-common = "dev-so"

FILES_${JDKPN}-jdk = " \
                       ${JDK_HOME}/bin \
                       ${JDK_HOME}/lib \
                       ${JDK_HOME}/include \
                      "
RDEPENDS_${JDKPN}-jre = "${JDKPN}-java ${JDKPN}-common"
RDEPENDS_${JDKPN}-java = "${JDKPN}-common"
RPROVIDES_${JDKPN}-jre = "java2-runtime"

RDEPENDS_${JDKPN}-jdk = "${JDKPN}-jre"

FILES_${JDKPN}-doc = "${JDK_HOME}/man"

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

require openjdk-postinst.inc

ALTERNATIVE_PRIORITY = "50"
