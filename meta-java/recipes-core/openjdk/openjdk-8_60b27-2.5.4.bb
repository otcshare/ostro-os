require openjdk-common.inc
ICEDTEA = "icedtea-${ICEDTEA_VERSION}"

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
  ${NASHORN_URI} \
  ${OEPATCHES} \
  ${ICEDTEAPATCHES} \
  file://jvm.cfg \
  "

JDKPN = "openjdk-8"
JDK_DIR = "java-8-openjdk"

PN = "${JDKPN}-jre"
PROVIDES += "${JDKPN} ${JDKPN}-jdk"

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
# java-runtime instead).
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

# For intel-core2-32 and Edison.
TUNE_CCARGS_append = "${@' -mstackrealign -fno-omit-frame-pointer' if '${TUNE_ARCH}' == 'i686' else ''}"

# disable shark until it is fully working again
# WITH_ADDITIONAL_VMS ?= "--with-additional-vms=shark,cacao,jamvm"

WITH_ADDITIONAL_VMS ?= "--with-additional-vms=cacao,jamvm"

# OpenJDK supports parallel compilation but uses a plain number for this.
# In OE we have PARALLEL_MAKE which is the actual option passed to make,
# e.g. "-j 4".

OPENJDK_PARALLEL_MAKE := "${PARALLEL_MAKE}"
PARALLEL_MAKE =  ""

def get_jdk8_jobs(d):
    import bb

    pm = bb.data.getVar('OPENJDK_PARALLEL_MAKE', d, 1);
    if not pm:
        return "1"

    pm = pm.split("j");
    if (len(pm) == 2):
        return pm[1].strip()

    # Whatever found in PARALLEL_MAKE was not suitable.
    return "1"

JDK_JOBS = "${@get_jdk8_jobs(d)}"

EXTRA_OECONF = " \
        --disable-tests \
        --disable-hotspot-tests \
        --disable-langtools-tests \
        --disable-jdk-tests \
        --disable-docs \
        --disable-nss \
        --disable-system-lcms \
        --disable-bootstrap \
        --with-rhino=${STAGING_DATADIR_JAVA}/rhino.jar \
        --with-jdk-home=${STAGING_LIBDIR_JVM_NATIVE}/icedtea7-native \
        --with-openjdk-src-zip=${WORKDIR}/${OPENJDK_FILE} \
        --with-hotspot-src-zip=${WORKDIR}/${HOTSPOT_FILE} \
        --with-corba-src-zip=${WORKDIR}/${CORBA_FILE} \
        --with-jaxp-src-zip=${WORKDIR}/${JAXP_FILE} \
        --with-jaxws-src-zip=${WORKDIR}/${JAXWS_FILE} \
        --with-jdk-src-zip=${WORKDIR}/${JDK_FILE} \
        --with-langtools-src-zip=${WORKDIR}/${LANGTOOLS_FILE} \
        --with-parallel-jobs=${JDK_JOBS} \
        --with-pkgversion=${PV} \
       "

do_configure_prepend() {
  bbnote "Copying and resetting patches...Configure with parallel-jobs: ${JDK_JOBS}"

  # Automatically copy everything that starts with "icedtea" (or "cacao") and ends with
  # ".patch" into the patches directory.
  find ${WORKDIR} -maxdepth 1 -name "icedtea*.patch" -exec cp {} ${S}/patches \;
  find ${WORKDIR} -maxdepth 1 -name "cacao*.patch" -exec cp {} ${S}/patches \;
  find ${WORKDIR} -maxdepth 1 -name "zero*.patch" -exec cp {} ${S}/patches \;
  find ${WORKDIR} -maxdepth 1 -name "faulty-nx-emulation.patch" -exec cp {} ${S}/patches \;
  # Overwrite pr2124.patch about NamedCurve.java
  > ${S}/patches/pr2124.patch 
  # Overwrite rhino.patch about JavaScript
  > ${S}/patches/rhino.patch 
  > ${S}/patches/boot/no.patch
  bbnote "No need to remove snmp etc.. from openjdk-8"
  > ${S}/fsg.sh.in        
}

do_configure_append() {
        # We are not removing any files from openjdk-8
        bbnote "Applying remaining patches.."
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
               '

# Provides the target architecture to the configure script.
export LLVM_CONFIGURE_ARCH="${@get_llvm_configure_arch(d)}"

OE_LAUNCHER_LDFLAGS = "-Wl,-rpath-link,${STAGING_LIBDIR}/llvm${WANT_LLVM_RELEASE} -Wl,-rpath,${libdir}/llvm${WANT_LLVM_RELEASE}"

OE_LAUNCHER_LDFLAGS_arm = ""

EXTRA_OEMAKE += 'OE_LAUNCHER_LDFLAGS="${OE_LAUNCHER_LDFLAGS}"'


OPENJDK_OECONF = " \
     --openjdk-target=${TARGET_SYS} \         
     --prefix=/usr                  \
     --exec_prefix=/usr             \
     --bindir=/usr/bin              \
     --sbindir=/usr/sbin            \
     --libexecdir=/usr/libexec      \
     --datadir=/usr/share           \
     --sysconfdir=/etc              \
     --sharedstatedir=/com          \
     --localstatedir=/var           \
     --libdir=/usr/lib              \
     --includedir=/usr/include      \
     --oldincludedir=/usr/include   \
     --infodir=/usr/share/info      \
     --mandir=/usr/share/man        \
     --disable-headful              \
     --with-sys-root=${STAGING_DIR_TARGET} \
     --with-boot-jdk=${STAGING_LIBDIR_JVM_NATIVE}/icedtea7-native \
     CFLAGS="--sysroot=${STAGING_DIR_TARGET} ${HOST_CC_ARCH}" \
     CXXFLAGS="--sysroot=${STAGING_DIR_TARGET} ${HOST_CC_ARCH}" \
     LDFLAGS="--sysroot=${STAGING_DIR_TARGET} " \
     --with-extra-cflags="--sysroot=${STAGING_DIR_TARGET} ${SELECTED_OPTIMIZATION} -DPNG_ARM_NEON_OPT=0" \
     --with-extra-cxxflags="--sysroot=${STAGING_DIR_TARGET} " \
     --with-extra-ldflags="--sysroot=${STAGING_DIR_TARGET} " \
     "

def should_build_zero(d):
    if (get_llvm_configure_arch(d) == "x86"):
        return False
    else:
        return True

def openjdk8_configuration(d):
    if (should_build_zero(d) == True):
        return "--with-jvm-variants=zero LIBFFI_LIBS=-lffi"
    else:
        return "--with-jvm-variants=server"

def openjdk_configuration(d):
    if (should_build_zero(d) == True):
        return "LIBFFI_LIBS=-lffi"
    else:
        return ""

# LIBFFI_LIBS needs to be in EXTRA_OECONF
OPENJDK_OECONF += "${@openjdk8_configuration(d)}"
EXTRA_OECONF += "${@openjdk_configuration(d)}"
BUILD_ZERO = "${@should_build_zero(d)}"

do_compile() {

        OPENJDK8_BUILD_LOC=`pwd`
        bbnote "3/3 Building final JDK @ ${OPENJDK8_BUILD_LOC}"
        # Create dummy Defs.gmk
        mkdir -p ${OPENJDK8_BUILD_LOC}/openjdk/jdk/make/common/
        mkdir -p ${OPENJDK8_BUILD_LOC}/openjdk/jdk/make/common/shared/
        > ${OPENJDK8_BUILD_LOC}/openjdk/jdk/make/common/shared/Defs.gmk

        # we do not want MAKE=make
        MAKE=/usr/bin/make
        BUILD_LD=/usr/bin/gcc
        ###############################################
        # Icedtea Makefile creates openjdk directory and copies various Java tar files etc.. and
        # and unpacks it...
        # This is where we need to configure OpenJDK-8
        ###############################################
        # Build the final Hotspot + OpenJDK
        #
        for F in `find ${TMPDIR}/work/${MULTIMACH_TARGET_SYS}/libffi -name sysroot-destdir`
        do
            #export LIBFFI_LIBS="-L${F}/usr/lib/ -lffi"
            LIBFFI_LOC=$F
        done
        for H in `find ${LIBFFI_LOC} -name include`
        do
            #export LIBFFI_CFLAGS="-I${H}/"
            ln -sf $H/ffi.h ${STAGING_INCDIR}/ffi.h 
            ln -sf $H/ffitarget.h ${STAGING_INCDIR}/ffitarget.h 
        done
        bbnote "We are trying to not apply patches to icedTea Makefile.am etc.."
        bbnote "This way changes to Makefile.am will not require us to regenerate patches..."
        if [ -e ${OPENJDK8_BUILD_LOC}/openjdk/configure ] ; then
          cd ${OPENJDK8_BUILD_LOC}/openjdk
          chmod +x ${OPENJDK8_BUILD_LOC}/openjdk/configure
          bbnote "Setting up NASHORN...."
          ln -sf ${WORKDIR}/${NASHORN_FILE} ${OPENJDK8_BUILD_LOC}/nashorn.tar.bz2 
          tar xf ${OPENJDK8_BUILD_LOC}/nashorn.tar.bz2 
          if [ -e nashorn ] ; then
              rm -rf nashorn
          fi;
          mv nashorn-${NASHORN_CHANGESET} nashorn
          if [ "${BUILD_ZERO}" = "True" ] ; then
              bbnote "Apply fixes to Openjdk source so that we can build Zero"
              if patch -l -p0 --dry-run -s -t -f -F 0 < ${S}/patches/zero-build.patch ;  
              then
                  bbnote "zero-build fix..."
                  patch -l -p0 < ${S}/patches/zero-build.patch
              else 
                  bbnote "Already patched for zero-build"
              fi;

              if patch -l -p0 --dry-run -s -t -f -F 0 < ${S}/patches/faulty-nx-emulation.patch ; 
              then
                  bbnote "faulty-nx-emulation fix"
                  patch -l -p0 < ${S}/patches/faulty-nx-emulation.patch
              else 
                  bbnote "Already patched for nx-emulation"
              fi;
          fi;

          bbnote "Configuring OpenJDK-8..."
          ${OPENJDK8_BUILD_LOC}/openjdk/configure ${OPENJDK_OECONF} 
        fi ;

        cd ${OPENJDK8_BUILD_LOC}                     
        cd openjdk

        rm -rf ${B}/${BUILD_DIR}

        bbnote "Building OpenJDK-8..."
        oe_runmake DEBUG_BINARIES=true all
        ############################################
        # Use following to create compact profiles.
        ############################################
        # For JRE only --- oe_runmake profiles
        # For JDK/JRE  --- oe_runmake images profiles
        
        cd build
        # Remove all debug symbol files.
        find . -name "*.diz" -exec rm {} \;

        ln -sf ${OPENJDK8_BUILD_LOC}/openjdk/build/*/images ${B}/${BUILD_DIR}
        echo ${B} ${BUILD_DIR} ${D}
        ls -al ${B}/${BUILD_DIR}
        cd ${OPENJDK8_BUILD_LOC}                     
        bbnote "Done with building Openjdk-8..."

        bbnote "Removing openjdk build created libjsig symlink"
        for libjsig_symbol in `find . -type l | grep libjsig.so` 
        do
            echo $libjsig_symbol
            cp --remove-destination `dirname $libjsig_symbol`/../libjsig.so $libjsig_symbol
        done
        pwd
        bbnote "Done fixing QA symlink issue"

        ############################################
        # Use following to copy compact profiles.
        ############################################
        # bbnote "Use following to copy compact3 profiles"

        # Copy comapct3 profile as JRE
        # cp -r images/j2re-compact3-image/bin ${B}/${BUILD_DIR}/j2sdk-image/jre/
        # cp -r images/j2re-compact3-image/lib ${B}/${BUILD_DIR}/j2sdk-image/jre/
        # Do the same for j2re-image
        # cp -r images/j2re-compact3-image/bin ${B}/${BUILD_DIR}/j2re-image/
        # cp -r images/j2re-compact3-image/lib ${B}/${BUILD_DIR}/j2re-image/



        # arm (beaglebone black) fix. JVM expects different name
        if [ "x${JDK_ARCH}x" = "xarmx" ]; then
          install -d -p ${D}/lib
          ln -sf ld-linux-armhf.so.3 ${D}/lib/ld-linux.so.3
        fi

}

# Part of arm fix: Add the symlink to the package
FILES_${PN}_arm_append = " /lib/ld-linux.so.3"


do_install() {

        install -d ${D}${libdir_jvm}
        cp -R ${B}/${BUILD_DIR}/j2sdk-image ${D}${JDK_HOME}

        chmod u+rw -R ${D}${JDK_HOME}

        # JRE is a subset of JDK, so to save space and resemble what the BIG distros
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
        ln -sf server/libjvm.so ${D}${JDK_HOME}/jre/lib/${JDK_ARCH}/
}

# Notes about the ideas behind packaging:
# 1) User should install openjdk-8-jre. This is a provider of 'java-runtime'.
# 2) This lets package mgmt install: openjdk-8-java
# openjdk-8-common
#
# For x86:
# We use hotspot VM as this is most optimal and fastest VM.
# For ARM:
# We use zero (interpreter mode) VM as hotspot is not yet compiling.
# 
# We need to install openjdk-8-jre for Java Runtime Support.
# To enable compiling on target, install openjdk-8-jdk package.
# 3) All other packages, including -jdk, are optional and not needed for normal Java apps.
#PACKAGES = " \
#            ${JDKPN}-jre \
#             ${JDKPN}-jre-dbg \
#            ${JDKPN}-dbg \
#            ${JDKPN}-demo-dbg \
#            ${JDKPN}-demo \
#            ${JDKPN}-source \
#            ${JDKPN}-doc \
#            ${JDKPN}-jdk \
#            ${JDKPN}-java \
#            ${JDKPN}-vm-shark \
#            ${JDKPN}-vm-zero \
#            ${JDKPN}-vm-cacao \
#             ${JDKPN}-vm-jamvm \
#            ${JDKPN}-common \
#           "

PACKAGES = " \
            ${JDKPN}-jre \
            ${JDKPN}-jdk \
            ${JDKPN}-java \
            ${JDKPN}-common \
            ${JDKPN}-src \
            ${JDKPN}-vm-server \
            ${JDKPN}-vm-client \
            ${JDKPN}-doc \
            ${JDKPN}-demo \
            ${JDKPN}-source \
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
RDEPENDS_${JDKPN}-demo = "java-runtime"
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

FILES_${JDKPN}-vm-server = "${JDK_HOME}/jre/lib/${JDK_ARCH}/server/"

FILES_${JDKPN}-vm-client = "${JDK_HOME}/jre/lib/${JDK_ARCH}/client/"

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

RDEPENDS_${JDKPN}-common = " freetype"

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
        ${JDK_HOME}/jre/bin/jjs \
       "


#RPROVIDES_${JDKPN}-vm-shark = "java2-vm"
#RPROVIDES_${JDKPN}-vm-zero = "java2-vm"
#RPROVIDES_${JDKPN}-vm-cacao = "java2-vm"
#RPROVIDES_${JDKPN}-vm-jamvm = "java2-vm"
#RPROVIDES_${JDKPN}-vm-jamvm = "java2-vm"

# Even though a vm is a hard dependency it is set as RRECOMMENDS so a single vm can get uninstalled:
# root@beaglebone:~/java# opkg remove openjdk-8-vm-shark
# No packages removed.
# Collected errors:
#  * print_dependents_warning: Package openjdk-8-vm-shark is depended upon by packages:
#  * print_dependents_warning:         openjdk-8-java
#  * print_dependents_warning: These might cease to work if package openjdk-8-vm-shark is removed.
#RRECOMMENDS_${JDKPN}-java = "java2-vm"

# For some reason shark and cacao do not automatically depends on -common.
# So we add that manually.
RDEPENDS_${JDKPN}-vm-shark = "${JDKPN}-common"
RDEPENDS_${JDKPN}-vm-cacao = "${JDKPN}-common"
RDEPENDS_${JDKPN}-vm-jamvm = "${JDKPN}-common"
# With out this you may see md5 mismatches.
RDEPENDS_${JDKPN}-common = "librhino-java"

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
RDEPENDS_${JDKPN}-jre = "${JDKPN}-java ${JDKPN}-common"
RDEPENDS_${JDKPN}-java = "${JDKPN}-common"
RPROVIDES_${JDKPN}-jre = "java-runtime java2-runtime"

RDEPENDS_${JDKPN}-jdk = "${JDKPN}-jre"

FILES_${JDKPN}-doc = "${JDK_HOME}/man"

require openjdk-postinst.inc

ALTERNATIVE_PRIORITY = "50"

LIC_FILES_CHKSUM = "file://COPYING;md5=59530bdf33659b29e73d4adb9f9f6552"

FILESPATH =. "${FILE_DIRNAME}/openjdk-8-60b27:"

# Name of the directory containing the compiled output
BUILD_DIR = "openjdk.build"
BUILD_DIR_ECJ = "openjdk.build-ecj"

ICEDTEA_URI = "http://icedtea.wildebeest.org/download/source/${ICEDTEA}.tar.gz;name=iced"

#ICEDTEA_PREFIX = "icedtea7-forest-2.5"
ICEDTEA_PREFIX = "jdk8u60"

OPENJDK_HG_URL = "http://hg.openjdk.java.net/jdk8u/jdk8u60"

OPENJDK_FILE = "${OPENJDK_CHANGESET}.tar.bz2"
OPENJDK_URI = "${OPENJDK_HG_URL}/archive/${OPENJDK_FILE};name=openjdk;unpack=false"

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

CACAO_VERSION = "e215e36be9fc"
CACAO_FILE = "${CACAO_VERSION}.tar.gz"
CACAO_URI = "http://icedtea.wildebeest.org/download/drops/cacao/${CACAO_FILE};name=cacao;unpack=false"
SRC_URI[cacao.md5sum] = "79f95f0aea4ba04cf2f1a8632ac66d14"
SRC_URI[cacao.sha256sum] = "4966514c72ee7ed108b882d9b6e65c3adf8a8f9c2dccb029f971b3c8cb4870ab"

JAMVM_VERSION = "ec18fb9e49e62dce16c5094ef1527eed619463aa"
JAMVM_FILE = "jamvm-${JAMVM_VERSION}.tar.gz"
JAMVM_URI = "http://icedtea.wildebeest.org/download/drops/jamvm/${JAMVM_FILE};name=jamvm;unpack=false"
SRC_URI[jamvm.md5sum] = "d50ae193d01a9251e10679c7a2cc6ff1"
SRC_URI[jamvm.sha256sum] = "31810266666c23822942aac62a78019c2c4589e1c5ee48329cbf42652d4437bc"

NASHORN_FILE = "${NASHORN_CHANGESET}.tar.bz2"
NASHORN_URI = "${OPENJDK_HG_URL}/nashorn/archive/${NASHORN_FILE};name=nashorn;unpack=false"

# Allow overriding this separately
OEPATCHES = "\
        file://fix-checksums.patch \
        file://cacao-libtoolize.patch \
        file://cacao-loadavg-makefile.patch \
        file://cacao-loadavg.patch;apply=no \
        file://cacao-arm-ucontext.patch;apply=no \
        file://zero-build.patch;apply=no \
        file://faulty-nx-emulation.patch;apply=no \
        "

ICEDTEAPATCHES = "\       
        file://icedtea-fix-galileo-build.patch;apply=no \
        file://icedtea-fix-zero-mode-undefined-behaviour.patch;apply=no \
        file://icedtea-fix-sdt-search-path.patch;apply=no \
        "

DISTRIBUTION_PATCHES = "\
        patches/icedtea-fix-galileo-build.patch \
        patches/icedtea-fix-zero-mode-undefined-behaviour.patch \
        patches/icedtea-fix-sdt-search-path.patch \
	"

export DISTRIBUTION_PATCHES

# overrride the jamvm patch for now, needs to be solved upstream
do_unpackpost() {
}

addtask unpackpost after do_unpack before do_patch

# Allow overriding this separately

# Allow overriding this separately

PR = "r0.1"

SRC_URI[iced.md5sum] = "646064d7a8d57c2cae0ef35a05de57c8"
SRC_URI[iced.sha256sum] = "5301b9a8592af2cf8e3e7a3650e5e1fe744c6d2de7f8ff78080b2eeae86a9800"

CORBA_CHANGESET = "be922f27d059"
SRC_URI[corba.md5sum] = "778ba99ed19c288d0d1b22f42d0c2107"
SRC_URI[corba.sha256sum] = "868083374cb6eb02ea5ab780f47702c224a50ea8dc7d9f67e10dcad9e731567d"

JAXP_CHANGESET = "56f6ca79467d"
SRC_URI[jaxp.md5sum] = "f8b291ba2a3c1e2964bd96328e0ebcfc"
SRC_URI[jaxp.sha256sum] = "254c622fc8a572efd0a10908b4038ba3cf41775d7c09c8f576800b3f608e33f7"

JAXWS_CHANGESET = "975eb04d1795"
SRC_URI[jaxws.md5sum] = "effc3c176b54d94042ef8351635c11d4"
SRC_URI[jaxws.sha256sum] = "eae19a40fdda776fc8bbe7f8f1ddbc8501d061026ffcd290b7cf8f9d7f8f0e20"

JDK_CHANGESET = "afbc08ea922b"
SRC_URI[jdk.md5sum] = "b65ffbe132d4efea2fab5c8ccd36693c"
SRC_URI[jdk.sha256sum] = "089850622aea0778ef73e8e43845952c4d21456075b61d2ed04fd3461c002925"

LANGTOOLS_CHANGESET = "e8e293d0db49"
SRC_URI[langtools.md5sum] = "35e388d87587131c28862fa244e99383"
SRC_URI[langtools.sha256sum] = "632183f6a948decdbd9f784a2742d4902ac2ab5c87b24232b02afa5f6efe6050"

OPENJDK_CHANGESET = "d50c3672fd18"
SRC_URI[openjdk.md5sum] = "afd33e3218e49f7ecb3c3f90088d9d94"
SRC_URI[openjdk.sha256sum] = "211d1a45b032066575e871ae4514f5db7f8313478a3ca9bad236c58e4892b48f"

# located in hotspot.map
HOTSPOT_CHANGESET = "10ad4b9d79f9"
SRC_URI[hotspot.md5sum] = "cf3ae34a7a4f1aec5fb8a895e3ebf2e4"
SRC_URI[hotspot.sha256sum] = "a95c0a8a20a90f387096dc37d52e4d1e42e5ac9da3c48fbe264d2fd5d79e9ae0"

NASHORN_CHANGESET = "72a33aed7dcc"
SRC_URI[nashorn.md5sum] = "ea2fdd450fbf186edf98619556eaa1ee"
SRC_URI[nashorn.sha256sum] = "36752f1ab4b1fb66fd8be412a8d2b1cfa9cf0258db743dc79e1e8c9607f50ef8"


INHIBIT_PACKAGE_DEBUG_SPLIT = "1"
INHIBIT_PACKAGE_STRIP = "1"

