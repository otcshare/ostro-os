SUMMARY = "Low Level Skeleton Library for Communication on Intel platforms"
SECTION = "libs"
AUTHOR = "Brendan Le Foll, Tom Ingleby"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://COPYING;md5=66493d54e65bfc12c7983ff2e884f37f"

S = "${WORKDIR}/git"

inherit distutils-base pkgconfig python-dir cmake

PACKAGES =+ "python-${PN} node-${PN} ${PN}-java"

PACKAGECONFIG ??= "python nodejs java"
PACKAGECONFIG[python] = "-DBUILDSWIGPYTHON=ON, -DBUILDSWIGPYTHON=OFF, swig-native python,"
PACKAGECONFIG[nodejs] = "-DBUILDSWIGNODE=ON, -DBUILDSWIGNODE=OFF, swig-native nodejs,"
PACKAGECONFIG[java] = "-DBUILDSWIGJAVA=ON, -DBUILDSWIGJAVA=OFF, swig-native icedtea7-native,"


# python-mraa package containing Python bindings
FILES_python-${PN} = "${PYTHON_SITEPACKAGES_DIR}/ \
                      ${datadir}/mraa/examples/python/ \
                      ${prefix}/src/debug/${BPN}/${PV}-${PR}/build/src/python/ \
                     "
RDEPENDS_python-${PN} += "python"
INSANE_SKIP_python-${PN} = "debug-files"

# node-mraa package containing Nodejs bindings
FILES_node-${PN} = "${libdir}/node_modules/ \
                    ${datadir}/mraa/examples/javascript/ \
                   "
RDEPENDS_node-${PN} += "nodejs"
INSANE_SKIP_node-${PN} = "debug-files"

# mraa-java package containing Java bindings
FILES_${PN}-java = "${libdir}/libmraajava.so \
                    ${datadir}/mraa/examples/java/ \
                    ${libdir}/pkgconfig/mraajava.pc \
                    ${prefix}/src/debug/${BPN}/${PV}-${PR}/build/src/java/ \
                    ${libdir}/.debug/libmraajava.so \
                   "
#                     ${libdir}/java/

RDEPENDS_${PN}-java += "java-runtime"
INSANE_SKIP_${PN}-java = "debug-files"


FILES_${PN}-doc += "${datadir}/mraa/examples/"

EXTRA_OECMAKE_append = "-DINSTALLGPIOTOOL=ON"

export JAVA_HOME="${STAGING_DIR}/${BUILD_SYS}/usr/lib/jvm/icedtea7-native"

cmake_do_generate_toolchain_file_append() {
  echo "
set (JAVA_AWT_INCLUDE_PATH ${JAVA_HOME}/include CACHE PATH \"AWT include path\" FORCE)
set (JAVA_AWT_LIBRARY ${JAVA_HOME}/jre/lib/amd64/libjawt.so CACHE FILEPATH \"AWT Library\" FORCE)
set (JAVA_INCLUDE_PATH ${JAVA_HOME}/include CACHE PATH \"java include path\" FORCE)
set (JAVA_INCLUDE_PATH2 ${JAVA_HOME}/include/linux CACHE PATH \"java include path\" FORCE)
set (JAVA_JVM_LIBRARY ${JAVA_HOME}/jre/lib/amd64/libjvm.so CACHE FILEPATH \"path to JVM\" FORCE)
" >> ${WORKDIR}/toolchain.cmake
}

do_compile_prepend () {
  # when yocto builds in ${D} it does not have access to ../git/.git so git
  # describe --tags fails. In order not to tag our version as dirty we use this
  # trick
  sed -i 's/-dirty//' src/version.c
}

