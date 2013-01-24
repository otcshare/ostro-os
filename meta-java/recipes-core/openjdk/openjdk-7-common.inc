DESCRIPTION = "Java runtime based upon the OpenJDK- and Icedtea Project"
HOMEPAGE = "http://icedtea.classpath.org"
LICENSE  = "GPL-2.0-with-classpath-exception"
PRIORITY = "optional"
SECTION  = "libs"

# Name of the icedtea tarball and top-level directory.
ICEDTEA = "NEEDS TO BE SET"

S = "${WORKDIR}/${ICEDTEA}"
B = "${S}/build"

INC_PR = "r4"

SRC_URI = " \
  ${ICEDTEA_URI} \
  ${OPENJDK_URI} \
  ${HOTSPOT_URI} \
  ${CORBA_URI} \
  ${JAXP_URI} \
  ${JAXWS_URI} \
  ${JDK_URI} \
  ${LANGTOOLS_URI} \
  ${CACAO_URI} \
  ${JAMVM_URI} \
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
           zlib \
	   jpeg libpng giflib \
           gtk+ glib-2.0 \
           cups fontconfig \
	   rhino \
	   libxt libxinerama libxrender libxtst libxi \
	   freetype alsa-lib libffi llvm2.8 \
          "
DEPENDS_arm = " \
           icedtea7-native zip-native ant-native \
           zlib \
           jpeg libpng giflib \
           gtk+ glib-2.0 \
           cups fontconfig \
           rhino \
           libxt libxinerama libxrender libxtst libxi \
           freetype alsa-lib libffi \
          "

DEPENDS_append_libc-uclibc = " virtual/libiconv "

# The OpenJDK build with interpreter optimizations for ARM depends on a binary
# that generates constants for an assembler source file. There is no other
# way than to generate this on a pseudo machine. Cross-compiling would not help
# because structure sizes and/or alignment may differ.
DEPENDS_append = " qemu-native "


# No package should directly depend on this (it should require
# java2-runtime instead).
PRIVATE_LIBS = "\
	libunpack.so libverify.so libjava.so libzip.so libnpt.so \
	libjava_crw_demo.so libhprof.so libnet.so libnio.so \
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
inherit java autotools gettext qemu

export ALT_CUPS_HEADERS_PATH = "${STAGING_INCDIR}"
export ALT_FREETYPE_HEADERS_PATH = "${STAGING_INCDIR}/freetype2"
export ALT_FREETYPE_LIB_PATH = "${STAGING_LIBDIR}"
export CACAO_CONFIGURE_ARGS = " \
	${@['','--enable-softfloat'][bb.data.getVar('TARGET_FPU',d,1) == 'soft']}"

JAVA_HOME[unexport] = "1"

# disable shark until it is fully working again
# WITH_ADDITIONAL_VMS ?= "--with-additional-vms=shark,cacao,jamvm"

WITH_ADDITIONAL_VMS ?= "--with-additional-vms=cacao,jamvm"

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
	--disable-pulse-java \
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
        ${WITH_ADDITIONAL_VMS} \
	--with-cacao-src-zip=${WORKDIR}/${CACAO_FILE} \
	--with-jamvm-src-zip=${WORKDIR}/${JAMVM_FILE} \
	\
	--with-parallel-jobs=${JDK_JOBS} \
	\
	--with-pkgversion=${PV} \
	--with-cc-for-build=${BUILD_CC} \
       "

# OpenJDK uses slightly different names for certain arches. We need to know
#	this to create some files which are expected by the build.
def get_jdk_arch(d):
    import bb

    jdk_arch = bb.data.getVar('TRANSLATED_TARGET_ARCH', d, 1)
    if jdk_arch == "x86-64":
        jdk_arch = "amd64"
    elif jdk_arch == "powerpc":
        jdk_arch = "ppc"
    elif jdk_arch == "powerpc64":
        jdk_arch = "ppc64"
    elif (jdk_arch == "i486" or jdk_arch == "i586" or jdk_arch == "i686"):
        jdk_arch = "i386"

    return jdk_arch

JDK_ARCH = "${@get_jdk_arch(d)}"
JDK_HOME = "${libdir_jvm}/${JDK_DIR}"
JDK_FAKE = "${WORKDIR}/fake-jdk"

# A function that is needed in the Shark builds.
def get_llvm_configure_arch(d):
    import bb;

    arch = bb.data.getVar('TRANSLATED_TARGET_ARCH', d, 1)
    if arch == "x86-64" or arch == "i486" or arch == "i586" or arch == "i686":
        arch = "x86"
    elif arch == "arm":
        arch = "arm"
    elif arch == "mipsel" or arch == "mips":
        arch = "mips"
    elif arch == "powerpc" or arch == "powerpc64":
        arch = "powerpc"
    else:
        bb.error("%s does not support %s yet" % (bb.data.getVar('PN', d, 1), arch) );

    return arch

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
EXTRA_OEMAKE = 'CC="${CC}" CCC="${CXX}" CPP="${CPP}" CXX="${CXX}" CC_FOR_BUILD="${BUILD_CC}"'

EXTRA_OEMAKE += ' \
                OE_CFLAGS="${TARGET_CFLAGS}" \
                OE_CPPFLAGS="${TARGET_CPPFLAGS}" \
                OE_CXXFLAGS="${TARGET_CXXFLAGS}" \
                OE_LDFLAGS="${TARGET_LDFLAGS}" \
                ZIPEXE="${STAGING_BINDIR_NATIVE}/zip" \
		CROSS_COMPILE_ARCH="${JDK_ARCH}" \
		REQUIRED_ALSA_VERSION="" \
               '

# Puts an OE specific string into the binary making it possible for the user
# to know where it comes from (and blame the right people ...).
DIST_ID = "Built for ${DISTRO}"
DIST_NAME = "${DISTRO}"
EXTRA_OEMAKE += 'DIST_NAME="${DIST_NAME}" DIST_ID="${DIST_ID}"'


# llvm configure and compiles stuff

export WANT_LLVM_RELEASE = "2.8"

# Provides the target architecture to the configure script.
export LLVM_CONFIGURE_ARCH="${@get_llvm_configure_arch(d)}"

OE_LAUNCHER_LDFLAGS = "-Wl,-rpath-link,${STAGING_LIBDIR}/llvm${WANT_LLVM_RELEASE} -Wl,-rpath,${libdir}/llvm${WANT_LLVM_RELEASE}"

OE_LAUNCHER_LDFLAGS_arm = ""

EXTRA_OEMAKE += 'OE_LAUNCHER_LDFLAGS="${OE_LAUNCHER_LDFLAGS}"'

# Large stack is required at least on x86_64 host, otherwise random segfaults appear:
QEMU = "${@qemu_target_binary(d)} ${QEMU_OPTIONS} -s 2097152 -L ${STAGING_DIR_TARGET} -E LD_LIBRARY_PATH=${STAGING_BASELIBDIR}"

EXTRA_OEMAKE += 'QEMU="${QEMU}"'

do_compile() {

	bbnote "3/3 Building final JDK"

	# Build the final Hotspot + OpenJDK
	oe_runmake icedtea-stage2
}

do_install() {
	install -d ${D}${libdir_jvm}
	cp -R ${S}/build/${BUILD_DIR}/j2sdk-image ${D}${JDK_HOME}

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
	${JDK_HOME}/jre/lib/${JDK_ARCH}/native_threads/.debug \
	${JDK_HOME}/jre/lib/${JDK_ARCH}/server/.debug \
        ${JDK_HOME}/jre/lib/${JDK_ARCH}/shark/.debug \
	${JDK_HOME}/jre/lib/${JDK_ARCH}/headless/.debug \
	${JDK_HOME}/jre/lib/${JDK_ARCH}/xawt/.debug \
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
                          ${JDK_HOME}/ASSEMBLY_EXCEPTION \
                          ${JDK_HOME}/THIRD_PARTY_README \
                          ${JDK_HOME}/LICENSE \
                          ${JDK_HOME}/release \
                          ${JDK_HOME}/jre/lib \
                         "

FILES_openjdk-7-jre_append = " \
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
# root@beaglebone:~/java# opkg remove openjdk-7-vm-shark
# No packages removed.
# Collected errors:
#  * print_dependents_warning: Package openjdk-7-vm-shark is depended upon by packages:
#  * print_dependents_warning: 	openjdk-7-java
#  * print_dependents_warning: These might cease to work if package openjdk-7-vm-shark is removed.
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
                      "
RDEPENDS_${JDKPN}-jre = "${JDKPN}-java"
RPROVIDES_${JDKPN}-jre = "java2-runtime"

RDEPENDS_${JDKPN}-jdk = "${JDKPN}-jre"

FILES_${JDKPN}-doc = "${JDK_HOME}/man"

pkg_postinst_${JDKPN}-vm-shark () {
        if grep -q "\-server ERROR" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg && ! grep -q "KNOWN" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg; then
          sed -i -e "/\-shark.*/d" -e "s|\(^\-server*\)|\-shark KNOWN\n\1|" -e "/^$/d" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
	else
          sed -i -e "s/\-shark.*/\-shark KNOWN/" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
        fi
}

pkg_prerm_${JDKPN}-vm-shark () {
	sed -i -e "/^\-shark.*/d" -e "/^$/d" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
        if grep -q "KNOWN" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg && grep -q "\-server ERROR" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg; then
          FIRST_KNOWN=`grep "KNOWN" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg | head -1`
          sed -i -e "/${FIRST_KNOWN}/d" -e  "s|\(^\-server*\)|${FIRST_KNOWN}\n\1|" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
        fi

        echo "-shark ERROR" >> ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
}

pkg_postinst_${JDKPN}-vm-cacao () {
        if grep -q "\-server ERROR" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg && ! grep -q "KNOWN" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg; then
          sed -i -e "/\-cacao.*/d" -e "s|\(^\-server*\)|\-cacao KNOWN\n\1|" -e "/^$/d" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
	else
          sed -i -e "s/\-cacao.*/\-cacao KNOWN/" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
        fi
}

pkg_prerm_${JDKPN}-vm-cacao () {
	sed -i -e "/^\-cacao.*/d" -e "/^$/d" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
        if grep -q "KNOWN" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg && grep -q "\-server ERROR" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg; then
          FIRST_KNOWN=`grep "KNOWN" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg | head -1`
          sed -i -e "/${FIRST_KNOWN}/d" -e  "s|\(^\-server*\)|${FIRST_KNOWN}\n\1|" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
        fi

        echo "-cacao ERROR" >> ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
}

pkg_postinst_${JDKPN}-vm-jamvm () {
        if grep -q "\-server ERROR" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg && ! grep -q "KNOWN" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg; then
          sed -i -e "/\-jamvm.*/d" -e "s|\(^\-server*\)|\-jamvm KNOWN\n\1|" -e "/^$/d" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
	else
          sed -i -e "s/\-jamvm.*/\-jamvm KNOWN/" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
        fi
}

pkg_prerm_${JDKPN}-vm-jamvm () {
	sed -i -e "/^\-jamvm.*/d" -e "/^$/d" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
        if grep -q "KNOWN" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg && grep -q "\-server ERROR" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg; then
          FIRST_KNOWN=`grep "KNOWN" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg | head -1`
          sed -i -e "/${FIRST_KNOWN}/d" -e  "s|\(^\-server*\)|${FIRST_KNOWN}\n\1|" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
        fi

        echo "-jamvm ERROR" >> ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
}

pkg_postinst_${JDKPN}-vm-zero () {
        if grep -q "KNOWN" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg && grep -q "\-server ERROR" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg; then
           FIRST_KNOWN=`grep "KNOWN" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg | head -1`
           sed -i -e "/${FIRST_KNOWN}/d" -e "/^$/d" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
           echo ${FIRST_KNOWN} >> $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
        fi

        sed -i -e "s|^\-server.*|\-server KNOWN|" -e "/^$/d" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
}

pkg_prerm_${JDKPN}-vm-zero () {
	sed -i -e "/^\-server.*/\-server ERROR" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
        if grep -q "KNOWN" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg; then
          FIRST_KNOWN=`grep "KNOWN" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg | head -1`
          sed -i -e "/${FIRST_KNOWN}/d" -e  "s|\(^\-server*\)|${FIRST_KNOWN}\n\1|" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
        fi
}

inherit update-alternatives

ALTERNATIVE_PRIORITY = "50"

ALTERNATIVE_${JDKPN}-jre = "java"
ALTERNATIVE_${JDKPN}-jdk = "javac"

ALTERNATIVE_LINK_NAME[java] = "${bindir}/java"
ALTERNATIVE_LINK_NAME[javac] = "${bindir}/javac"

