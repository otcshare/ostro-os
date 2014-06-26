require openjdk-common.inc

ICEDTEA = "icedtea6-${ICEDTEA_VERSION}"

INC_PR = "r22"

SRC_URI = "\
  ${ICEDTEA_URI} \
  ${OPENJDK_URI} \
  ${JAXWS_URI} \
  ${JAF_URI} \
  ${JAXP_URI} \
  ${CACAO_URI} \
  ${JAMVM_URI} \
  ${OEPATCHES} \
  ${ICEDTEAPATCHES} \
  file://jvm.cfg \
  "

JDKPN = "openjdk-6"
JDK_DIR = "java-6-openjdk"

PN = "${JDKPN}-jre"
PROVIDES += "${JDKPN} ${PACKAGES}"

DEPENDS = "giflib libpng jpeg cups \
	   rhino \
	   freetype libxinerama libxt libxrender libxtst libxi \
	   alsa-lib libffi \
           ant-native \
           fastjar-native \
	   icedtea6-native \
           zip-native \
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
export CACAO_CONFIGURE_ARGS = "\
	${@['','--enable-softfloat'][bb.data.getVar('TARGET_FPU',d,1) == 'soft']}"

JAVA_HOME[unexport] = "1"

EXTRA_OECONF = "\
	--disable-docs \
	--disable-pulse-java \
	\
	--with-ecj-jar=${STAGING_DATADIR_JAVA_NATIVE}/ecj-bootstrap.jar \
	--with-java=${STAGING_LIBDIR_JVM_NATIVE}/icedtea6-native/bin/java \
	--with-javac=${STAGING_LIBDIR_JVM_NATIVE}/icedtea6-native/bin/javac \
	--with-javah=${STAGING_LIBDIR_JVM_NATIVE}/icedtea6-native/bin/javah \
	--with-jar=${STAGING_LIBDIR_JVM_NATIVE}/icedtea6-native/bin/jar \
	--with-rmic=${STAGING_LIBDIR_JVM_NATIVE}/icedtea6-native/bin/rmic \
	--with-native2ascii=${STAGING_LIBDIR_JVM_NATIVE}/icedtea6-native/bin/native2ascii \
	--with-rhino=${STAGING_DATADIR_JAVA}/rhino.jar \
	--without-ant-home \
	--with-openjdk-src-dir=${WORKDIR}/openjdk-src-dir \
	--with-parallel-jobs=${JDK_JOBS} \
	\
	--with-pkgversion=${PV} \
	--with-cc-for-build=${BUILD_CC} \
        --enable-zero \
        --with-additional-vms=${WITH_ADDITIONAL_VMS} \
        --enable-openjdk-cross-compilation \
       "


# OpenJDK supports parallel compilation but uses a plain number for this.
# In OE we have PARALLEL_MAKE which is the actual option passed to make,
# e.g. "-j 4".
def get_jdk_jobs(d):
    import bb

    pm = bb.data.getVar('PARALLEL_MAKE', d, 1);
    if not pm:
        return "1"

    pm = pm.split("j");
    if (len(pm) == 2):
        return pm[1]

    # Whatever found in PARALLEL_MAKE was not suitable.
    return "1"

JDK_JOBS = "${@get_jdk_jobs(d)}"

# Custom preparation of the sources which:
# - cleans up the sources
# - copies the patches into the proper directory
# - prepares the FakeJDK directory structure
#DISABLED because of incompatibility with oe stable 2009: do_prepareconfigure () {
do_configure_prepend() {
  chmod -R ug+w ${WORKDIR}/openjdk-src-dir
  (cd ${WORKDIR}/openjdk-src-dir && sh ${S}/fsg.sh)

  # Automatically copy everything that starts with "icedtea" (or "cacao") and ends with
  # ".patch" into the patches directory.
  find ${WORKDIR} -maxdepth 1 -name "icedtea*.patch" -exec cp {} ${S}/patches \;
  find ${WORKDIR} -maxdepth 1 -name "cacao*.patch" -exec cp {} ${S}/patches \;

  # use now the rt.jar from icedtea6-native
  mkdir -p ${WORKDIR}/fake-jdk/jre/lib
  ln -sf ${STAGING_LIBDIR_JVM_NATIVE}/icedtea6-native/jre/lib/rt.jar ${WORKDIR}/fake-jdk/jre/lib/rt.jar

  symlinked=false
  bbnote "Creating symlinks for fake-jdk"
  mkdir -p ${WORKDIR}/fake-jdk/include
  for i in `find ${STAGING_LIBDIR_JVM_NATIVE}/icedtea6-native/include` ;do
	bn=`basename $i`
	echo "Symlinking: $bn"
    ln -sf $i ${WORKDIR}/fake-jdk/include/$bn;
	symlinked=true
  done

  # If the symlinks have not been created the built cannot continue. This
  # can happen if icedtea6-native is not ready at this point. The recipe
  # should make sure this is not the case but a little sanity checking
  # in such a complicated build can't be wrong.
  if [ x$symlinked = xfalse ]
  then
    bberror "Build b0rken! Have not created any symlinks for fake-jdk!"
  else
    bbnote "fake-jdk setup appears sane."
  fi
}

# Note: The following lines only work for OE.dev branch but cause an exception
# in oe stable's 2009 bitbake. As such the function is prepended to do_configure instead.
#addtask prepareconfigure after do_patch before do_configure
# Makes prepareconfigure depend on icedtea6-native having being staged.
#do_prepareconfigure[depends] += "icedtea6-native:do_populate_sysroot"


do_configure_append() {
	oe_runmake patch-ecj
}

# Work around broken variable quoting in oe-stable 2009 and provide the variable
# via the environment which then overrides the erroneous value that was written
# into '${ICETDEA}/Makefile'.
# Icedtea's makefile is not compatible to parallelization so we cannot allow
# passing a valid ${PARALLEL_MAKE} to it. OTOH OpenJDK's makefiles are
# parallelizable and we need ${PARALLEL_MAKE} to derive the proper value.
# The base for this quirk is that GNU Make only considers the last "-j" option.
EXTRA_OEMAKE += '-j 1 CC="${CC}" CCC="${CXX}" CPP="${CPP}" CXX="${CXX}" CC_FOR_BUILD="${BUILD_CC}"'

EXTRA_OEMAKE += ' \
                OE_CFLAGS="${TARGET_CFLAGS}" \
                OE_CPPFLAGS="${TARGET_CPPFLAGS}" \
                OE_CXXFLAGS="${TARGET_CXXFLAGS}" \
                OE_LDFLAGS="${TARGET_LDFLAGS}" \
                ZIPEXE="${STAGING_BINDIR_NATIVE}/zip" \
               '

OE_LAUNCHER_LDFLAGS = "-Wl,-rpath-link,${STAGING_LIBDIR}/llvm${WANT_LLVM_RELEASE} -Wl,-rpath,/usr/lib/llvm${WANT_LLVM_RELEASE}"

EXTRA_OEMAKE += 'OE_LAUNCHER_LDFLAGS="${OE_LAUNCHER_LDFLAGS}"'


# The build of OpenJDK is a 3-part process. For better restartability and overrideability they have been split into
# three functions.
# 1. compile Hotspot or Cacao (this one is supposed to be implemented according to wanted VM)
# 2. compile openjdk-ecj (to have libraries as libjvm.so and libjava.so which are needed later)
# 3. compile openjdk (the final result)

do_compilestepone() {
        oe_runmake bootstrap-directory-ecj

        # now we need to override the tools.jar to point to the normal jdk's tools.jar
        rm bootstrap/ecj/lib/tools.jar
        ln -s ${STAGING_LIBDIR_JVM_NATIVE}/icedtea6-native/lib/tools.jar bootstrap/ecj/lib/tools.jar

        # First build hotspot to get a libjvm.so (to link corba in the icedtea-ecj build)
        bbnote "1/3 Building Hotspot"
        oe_runmake hotspot

        # Remove spurious libarch directory/symlink
        rm -rf bootstrap/ecj/jre/lib/${JDK_ARCH} || true

                # Provide a symlink to the target arch's libjvm.so (to link against)
        ln -s `pwd`/${BUILD_DIR_ECJ}/j2sdk-image/jre/lib/${JDK_ARCH} bootstrap/jdk1.6.0/jre/lib/${JDK_ARCH}

        # fake j2sdk-image
        rm ${BUILD_DIR_ECJ}/j2sdk-image/include || true
        cp -ar ${BUILD_DIR_ECJ}/hotspot/import/include ${BUILD_DIR_ECJ}/j2sdk-image/
        install -d ${BUILD_DIR_ECJ}/j2sdk-image/bin
}
addtask compilestepone after do_configure before do_compilesteptwo

# This part can be shared between cacao and hotspot-zero builds.
do_compilesteptwo() {
	bbnote "2/3 Building bootstrap JDK"

	# Now cross-compile bootstrap JDK
	rm stamps/icedtea-against-ecj.stamp stamps/icedtea-ecj.stamp || true
	oe_runmake icedtea-against-ecj

	ln -sf ../${BUILD_DIR_ECJ}/j2sdk-image bootstrap/icedtea

	#	Replace all executables with symlinks to their native equivalents.
	for F in `find ${STAGING_LIBDIR_JVM_NATIVE}/icedtea6-native/bin -type f`
	do
		bf=`basename $F`
		bbnote "Creating symlink for:" $bf
		ln -sf $F bootstrap/icedtea/bin/$bf
	done
}
addtask compilesteptwo after do_compilestepone before do_compile

do_compile() {

	bbnote "3/3 Building final JDK"

	# Build the final Hotspot + OpenJDK
	oe_runmake icedtea-against-icedtea
}

do_install() {
	install -d ${D}${libdir_jvm}
	cp -R ${WORKDIR}/build/${BUILD_DIR}/j2sdk-image ${D}${JDK_HOME}

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
# 1) User should install openjdk-6-jre. This is a provider of 'java2-runtime'.
# 2) This lets package mgmt install: openjdk-6-java
# -> openjdk-6-vm-shark|openjdk-6-vm-zero|openjdk-6-vm-cacao -> openjdk-6-common
#
# With opkg the zero VM is chosen which is good b/c that is the best known (= compatible)
# runtime. Installing other runtimes side-by-side is possible. Through jvm.cfg the following
# order of precedence is enforced: zero, shark, cacao. User can chose a different runtime
# by adding '-shark' or '-cacao' to the Java command (or by deinstalling an otherwise preferred
# runtime)
# 3) All other packages, including -jdk, are optional and not needed for normal Java apps.
PACKAGES = " \
            ${JDKPN}-jre \
            ${JDKPN}-dbg \
            ${JDKPN}-demo-dbg \
            ${JDKPN}-demo \
            ${JDKPN}-source \
            ${JDKPN}-doc \
            ${JDKPN}-jdk \
            ${JDKPN}-java \
            ${JDKPN}-vm-shark \
            ${JDKPN}-vm-zero \
            ${JDKPN}-vm-cacao \
	    ${JDKPN}-vm-jamvm \
            ${JDKPN}-common \
           "

FILES_${JDKPN}-dbg = "\
	${JDK_HOME}/bin/.debug \
	${JDK_HOME}/lib/.debug \
	${JDK_HOME}/jre/bin/.debug \
	${JDK_HOME}/jre/lib/.debug \
	${JDK_HOME}/jre/lib/${JDK_ARCH}/.debug \
	${JDK_HOME}/jre/lib/${JDK_ARCH}/jli/.debug \
	${JDK_HOME}/lib/${JDK_ARCH}/jli/.debug \
	${JDK_HOME}/jre/lib/${JDK_ARCH}/native_threads/.debug \
	${JDK_HOME}/jre/lib/${JDK_ARCH}/server/.debug \
        ${JDK_HOME}/jre/lib/${JDK_ARCH}/shark/.debug \
        ${JDK_HOME}/jre/lib/${JDK_ARCH}/cacao/.debug \
        ${JDK_HOME}/jre/lib/${JDK_ARCH}/jamvm/.debug \
	${JDK_HOME}/jre/lib/${JDK_ARCH}/headless/.debug \
	${JDK_HOME}/jre/lib/${JDK_ARCH}/xawt/.debug \
	/usr/src \
       "

FILES_${JDKPN}-demo = "${JDK_HOME}/demo ${JDK_HOME}/sample"
RDEPENDS_${JDKPN}-demo = "java2-runtime"
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

FILES_${JDKPN}-vm-shark = "${JDK_HOME}/jre/lib/${JDK_ARCH}/shark/"

FILES_${JDKPN}-vm-cacao = "${JDK_HOME}/jre/lib/${JDK_ARCH}/cacao/"

FILES_${JDKPN}-vm-jamvm = "${JDK_HOME}/jre/lib/${JDK_ARCH}/jamvm/"

FILES_${JDKPN}-common = "${JDK_HOME}/jre/ASSEMBLY_EXCEPTION \
                          ${JDK_HOME}/jre/THIRD_PARTY_README \
                          ${JDK_HOME}/jre/LICENSE \
                          ${JDK_HOME}/jre/lib \
                         "

FILES_openjdk-6-jre_append = " \
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

RPROVIDES_${JDKPN}-vm-shark = "java2-vm"
RPROVIDES_${JDKPN}-vm-zero = "java2-vm"
RPROVIDES_${JDKPN}-vm-cacao = "java2-vm"
RPROVIDES_${JDKPN}-vm-jamvm = "java2-vm"

# Even though a vm is a hard dependency it is set as RRECOMMENDS so a single vm can get uninstalled:
# root@beaglebone:~/java# opkg remove openjdk-6-vm-shark
# No packages removed.
# Collected errors:
#  * print_dependents_warning: Package openjdk-6-vm-shark is depended upon by packages:
#  * print_dependents_warning: 	openjdk-6-java
#  * print_dependents_warning: These might cease to work if package openjdk-6-vm-shark is removed.
RRECOMMENDS_${JDKPN}-java = "java2-vm"

# For some reason shark and cacao do not automatically depends on -common.
# So we add that manually.
RDEPENDS_${JDKPN}-vm-shark = "${JDKPN}-common"
RDEPENDS_${JDKPN}-vm-cacao = "${JDKPN}-common"
RDEPENDS_${JDKPN}-vm-jamvm = "${JDKPN}-common"

# There is a symlink to a .so but this one is valid.
INSANE_SKIP_${JDKPN}-vm-shark = "dev-so"
INSANE_SKIP_${JDKPN}-vm-zero = "dev-so"
INSANE_SKIP_${JDKPN}-vm-cacao = "dev-so"
INSANE_SKIP_${JDKPN}-vm-jamvm = "dev-so"
INSANE_SKIP_${JDKPN}-common = "dev-so"

FILES_${JDKPN}-jdk = " \
                       ${JDK_HOME}/bin \
                       ${JDK_HOME}/lib \
                       ${JDK_HOME}/include \
                       ${JDK_HOME}/ASSEMBLY_EXCEPTION \
                       ${JDK_HOME}/THIRD_PARTY_README \
                       ${JDK_HOME}/LICENSE \
                      "
RDEPENDS_${JDKPN}-jre = "${JDKPN}-java"
RPROVIDES_${JDKPN}-jre = "java2-runtime"

RDEPENDS_${JDKPN}-jdk = "${JDKPN}-jre"

FILES_${JDKPN}-doc = "${JDK_HOME}/man"

require openjdk-postinst.inc

ALTERNATIVE_PRIORITY = "20"
