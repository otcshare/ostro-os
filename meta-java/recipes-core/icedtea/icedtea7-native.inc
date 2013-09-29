DESCRIPTION = "Harness to build the source code from OpenJDK using Free Software build tools"
HOMEPAGE = "http://icedtea.classpath.org"
LICENSE  = "GPL-2.0-with-classpath-exception"
INC_PR = "r1"

DEPENDS = "virtual/javac-native virtual/java-native classpath-native \
           rhino-native ant-native \
           libx11-native xproto-native libxt-native libxext-native libxrender-native \
           giflib-native jpeg-native libpng-native \
           glib-2.0-native freetype-native zlib-native \
           fontconfig-native zip-native alsa-lib-native \
	   unzip-native \
          "

inherit native java autotools

JAVA_HOME[unexport] = "1"

SRC_URI = " \
  ${ICEDTEA_URI} \
  ${OPENJDK_URI} \
  ${HOTSPOT_URI} \
  ${CORBA_URI} \
  ${JAXP_URI} \
  ${JAXWS_URI} \
  ${JDK_URI} \
  ${LANGTOOLS_URI} \
  ${ICEDTEA_PATCHES} \
  ${OPENJDK_PATCHES} \
  "

S = "${WORKDIR}/${ICEDTEA}"
B = "${S}/build"

# openjdk looks in /usr/include and /usr/lib for freetype by default.
export ALT_FREETYPE_HEADERS_PATH = "${STAGING_INCDIR}/freetype2"
export ALT_FREETYPE_LIB_PATH = "${STAGING_LIBDIR}"

# OpenJDK supports parallel compilation but uses a plain number for this.
# In OE we have PARALLEL_MAKE which is the actual option passed to make,
# e.g. "-j 4".
ICEDTEA_PARALLEL_MAKE := "${PARALLEL_MAKE}"
PARALLEL_MAKE = ""
def get_jdk7_native_jobs(d):
    import bb

    pm = bb.data.getVar('ICEDTEA_PARALLEL_MAKE', d, 1);
    if not pm:
        return "1"

    pm = pm.split("j");
    if (len(pm) == 2):
        return pm[1].strip()

    # Whatever found in PARALLEL_MAKE was not suitable.
    return "1"

EXTRA_OECONF = "\
	--with-parallel-jobs=${@get_jdk7_native_jobs(d)} \
	\
        --disable-tests \
        --disable-hotspot-tests \
        --disable-langtools-tests \
        --disable-jdk-tests \
        --disable-pulse-java \
        --disable-docs \
        --disable-nss \
        --disable-system-lcms \
	--disable-system-gtk \
	\
	--with-jdk-home=${WORKDIR}/fake-jdk \
	--with-javac=${STAGING_BINDIR_NATIVE}/javac \
	--with-rhino=${STAGING_DATADIR_NATIVE}/java/rhino.jar \
	\
	--with-openjdk-src-zip=${DL_DIR}/${OPENJDK_FILE} \
        --with-hotspot-src-zip=${DL_DIR}/${HOTSPOT_FILE} \
        --with-corba-src-zip=${DL_DIR}/${CORBA_FILE} \
        --with-jaxp-src-zip=${DL_DIR}/${JAXP_FILE} \
        --with-jaxws-src-zip=${DL_DIR}/${JAXWS_FILE} \
        --with-jdk-src-zip=${DL_DIR}/${JDK_FILE} \
        --with-langtools-src-zip=${DL_DIR}/${LANGTOOLS_FILE} \
  "

JDK_DIR = "icedtea7-native"

JDK_INSTALL_DIR = "${D}/${libdir_jvm}/${JDK_DIR}"

do_configure_prepend() {
        case "${TRANSLATED_TARGET_ARCH}" in
                x86-64)
                        libarch=amd64
                ;;
                i386|i486|i586|i686)
                        libarch=x86
                ;;
                *)
                        arch=${TARGET_ARCH}
                        libarch=${TARGET_ARCH}
                ;;
        esac

	# Automatically copy everything that starts with "icedtea" and ends with
	# ".patch" into the patches directory.
	find ${WORKDIR} -maxdepth 1 -name "icedtea*.patch" -exec cp {} ${S}/patches \;

	# Prepare JDK-like directory with Classpath' files which we can treat as a
	# SYSTEM_GCJ_DIR afterwards.
	mkdir -p ${WORKDIR}/fake-jdk/jre/lib/
	ln -sf ${STAGING_DATADIR_NATIVE}/classpath/glibj.zip ${WORKDIR}/fake-jdk/jre/lib/rt.jar

        mkdir -p ${WORKDIR}/fake-jdk/bin
        ln -sf ${STAGING_BINDIR_NATIVE}/java  ${WORKDIR}/fake-jdk/bin/java
	#ln -sf ${STAGING_BINDIR_NATIVE}/javac ${WORKDIR}/fake-jdk/bin/javac
	ln -sf ${STAGING_BINDIR_NATIVE}/gjavah ${WORKDIR}/fake-jdk/bin/javah
	ln -sf ${STAGING_BINDIR_NATIVE}/gjar  ${WORKDIR}/fake-jdk/bin/jar
	ln -sf ${STAGING_BINDIR_NATIVE}/grmic ${WORKDIR}/fake-jdk/bin/rmic
        ln -sf ${STAGING_BINDIR_NATIVE}/gnative2ascii ${WORKDIR}/fake-jdk/bin/native2ascii

	mkdir -p ${WORKDIR}/fake-jdk/include
	for i in ${STAGING_INCDIR_NATIVE}/classpath/* ;do
		test -r $i | continue;
		bn=`basename $i`
		ln -sf $i ${WORKDIR}/fake-jdk/include/$bn;
	done
}

do_configure_append() {
	oe_runmake patch-fsg

	for F in openjdk/jdk/make/common/shared/Compiler-gcc.gmk ;
	do
		sed -i \
			-e"s|\$(COMPILER_PATH)gcc\$(GCC_SUFFIX)|${CC}|" \
			-e"s|\$(COMPILER_PATH)gcc\$(GCC_SUFFIX) -E|${CPP}|" \
			-e"s|\$(COMPILER_PATH)g++\$(GCC_SUFFIX)|${CXX}|" \
			$F
	done

	for F in openjdk/hotspot/make/linux/makefiles/gcc.make openjdk/hotspot/agent/src/os/linux/Makefile ;
	do
		sed -i \
			-e"s|gcc\$(GCC_SUFFIX)|${CC}|" \
			-e"s|g++\$(GCC_SUFFIX)|${CXX}|" \
			$F
	done
	oe_runmake patch-boot
}

EXTRA_OEMAKE = ' \
                OE_CFLAGS="${CFLAGS}" \
                OE_CPPFLAGS="${CPPFLAGS}" \
                OE_CXXFLAGS="${CXXFLAGS}" \
                OE_LDFLAGS="${LDFLAGS}" \
                ZIPEXE="${STAGING_BINDIR_NATIVE}/zip" \
               '

do_compile() {
	# OpenJDK uses slightly different names for certain arches. We need to know
	#	this to create some files which are expected by the build.
	case "${TRANSLATED_TARGET_ARCH}" in
		x86-64)
			arch=amd64
			libarch=amd64
		;;
		i386|i486|i586|i686)
			arch=x86
			libarch=x86
		;;
		*)
			arch=${TARGET_ARCH}
			libarch=${TARGET_ARCH}
		;;
	esac

        install -d openjdk-boot/control/build/linux-$arch/hotspot/import/jre/lib
        if [ $libarch != $arch ]; then
                # Something is strange with the directoy naming. OpenJDK uses both variants.
                ln -sf $libarch openjdk-boot/control/build/linux-$arch/hotspot/import/jre/lib/$arch
        fi

        common_dirs="openjdk.build-boot/tmp/sun openjdk.build/tmp/sun"
	for CM in ${common_dirs}
	do
          for DM in javax.sound/jsoundalsa sun.awt.X11/xawt sun.awt/jawt;
          do
                bbnote "creating ${CM}/${DM}/obj64/.files_compiled"
                install -d ${CM}/${DM}/obj64
                touch ${CM}/${DM}/obj64/.files_compiled

                bbnote "creating ${CM}/${DM}/obj/.files_compiled"
                install -d ${CM}/${DM}/obj
                touch ${CM}/${DM}/obj/.files_compiled
          done
        done

        # Now cross-compile bootstrap JDK
        oe_runmake icedtea
}

def jdk_arch(d):
        import bb

        target_arch = bb.data.getVar('TRANSLATED_TARGET_ARCH', d, 1)

        if target_arch in ['i386', 'i486', 'i586', 'i686']:
            return "x86"
        elif target_arch in ['x86-64']:
            return "amd64"

        return target_arch

do_install() {
	case "${TRANSLATED_TARGET_ARCH}" in
		x86-64)
			JDK_ARCH=amd64
		;;
		i386|i486|i586|i686)
			JDK_ARCH=x86
		;;
		*)
			JDK_ARCH=${TARGET_ARCH}
		;;
	esac

	install -d ${JDK_INSTALL_DIR}

	SDKDIR=openjdk.build/j2sdk-image
	for F in ${SDKDIR}/bin ${SDKDIR}/include ${SDKDIR}/jre ${SDKDIR}/lib
	do
		cp -RL $F ${JDK_INSTALL_DIR}
	done

	#cp openjdk-boot/jdk/src/solaris/hpi/export/*.h ${JDK_INSTALL_DIR}/include/hpi
	#cp openjdk-boot/jdk/src/share/hpi/export/*.h ${JDK_INSTALL_DIR}/include/hpi

	install -d ${JDK_INSTALL_DIR}/include/javavm
	cp openjdk-boot/jdk/src/share/javavm/export/*.h ${JDK_INSTALL_DIR}/include/javavm
	cp openjdk-boot/jdk/src/solaris/javavm/export/*.h ${JDK_INSTALL_DIR}/include/javavm

	# Fix libjvm.so dependency of libfontmanager.so
	ln -sf server/libjvm.so ${JDK_INSTALL_DIR}/jre/lib/${JDK_ARCH}/libjvm.so
	ln -sf server/libjvm.so ${JDK_INSTALL_DIR}/jre/lib/${JDK_ARCH}/libjvm.so.0

	# Fix missing write permissions on the files.
	chmod ug+w -R ${JDK_INSTALL_DIR}
}

get_jdk7_native_jobs[vardepsexclude] += "ICEDTEA_PARALLEL_MAKE"
