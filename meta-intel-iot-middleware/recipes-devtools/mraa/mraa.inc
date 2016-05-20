SUMMARY = "Low Level Skeleton Library for Communication on Intel platforms"
SECTION = "libs"
AUTHOR = "Brendan Le Foll, Tom Ingleby"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://COPYING;md5=66493d54e65bfc12c7983ff2e884f37f"

S = "${WORKDIR}/git"

inherit distutils-base pkgconfig python-dir cmake

EXTRA_OECMAKE_append = "-DINSTALLGPIOTOOL=ON -DPYTHON_SITE_DIR:FILEPATH=${PYTHON_SITEPACKAGES_DIR} -DBASE_LIB_INSTALL_DIR=${base_libdir} -DCMAKE_SKIP_RPATH=ON"

FILES_${PN}-doc += "${datadir}/mraa/examples/"

PACKAGECONFIG ??= "python nodejs java"
PACKAGECONFIG[python] = "-DBUILDSWIGPYTHON=ON, -DBUILDSWIGPYTHON=OFF, swig-native python,"
PACKAGECONFIG[nodejs] = "-DBUILDSWIGNODE=ON, -DBUILDSWIGNODE=OFF, swig-native nodejs,"
PACKAGECONFIG[java] = "-DBUILDSWIGJAVA=ON, -DBUILDSWIGJAVA=OFF, swig-native openjdk-8-native,"

do_compile_prepend () {
  # when yocto builds in ${D} it does not have access to ../git/.git so git
  # describe --tags fails. In order not to tag our version as dirty we use this
  # trick
  sed -i 's/-dirty//' src/version.c
}


### Python ###

# python-mraa package containing Python bindings
FILES_python-${PN} = "${PYTHON_SITEPACKAGES_DIR}/ \
                      ${datadir}/mraa/examples/python/ \
                      ${prefix}/src/debug/${BPN}/${PV}-${PR}/build/src/python/ \
                     "
RDEPENDS_python-${PN} += "python"
INSANE_SKIP_python-${PN} = "debug-files"


### Node ###

# node-mraa package containing Nodejs bindings
FILES_node-${PN} = "${libdir}/node_modules/ \
                    ${datadir}/mraa/examples/javascript/ \
                   "
RDEPENDS_node-${PN} += "nodejs"
INSANE_SKIP_node-${PN} = "debug-files"


### Java ###

# mraa-java package containing Java bindings
FILES_${PN}-java = "${libdir}/libmraajava.so \
                    ${libdir}/java/ \
                    ${datadir}/mraa/examples/java/ \
                    ${libdir}/pkgconfig/mraajava.pc \
                    ${prefix}/src/debug/${BPN}/${PV}-${PR}/build/src/java/ \
                    ${libdir}/.debug/libmraajava.so \
                   "

RDEPENDS_${PN}-java += "java2-runtime"
INSANE_SKIP_${PN}-java = "debug-files"

export JAVA_HOME="${STAGING_DIR}/${BUILD_SYS}/usr/lib/jvm/openjdk-8-native"

cmake_do_generate_toolchain_file_append() {
  echo "
set (JAVA_AWT_INCLUDE_PATH ${JAVA_HOME}/include CACHE PATH \"AWT include path\" FORCE)
set (JAVA_AWT_LIBRARY ${JAVA_HOME}/jre/lib/amd64/libjawt.so CACHE FILEPATH \"AWT Library\" FORCE)
set (JAVA_INCLUDE_PATH ${JAVA_HOME}/include CACHE PATH \"java include path\" FORCE)
set (JAVA_INCLUDE_PATH2 ${JAVA_HOME}/include/linux CACHE PATH \"java include path\" FORCE)
set (JAVA_JVM_LIBRARY ${JAVA_HOME}/jre/lib/amd64/libjvm.so CACHE FILEPATH \"path to JVM\" FORCE)
" >> ${WORKDIR}/toolchain.cmake
}



### Include language bindings ###

PACKAGES =+ "python-${PN} node-${PN} ${PN}-java"

