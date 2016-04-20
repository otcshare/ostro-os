SUMMARY = "Sensor/Actuator repository for Mraa"
SECTION = "libs"
AUTHOR = "Brendan Le Foll, Tom Ingleby, Yevgeniy Kiveisha"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=d1cc191275d6a8c5ce039c75b2b3dc29"

DEPENDS = "nodejs swig-native mraa"

SRC_URI = "git://github.com/intel-iot-devkit/upm.git;protocol=git;rev=655ccee9afd259bff1773e9e8aea860f6e06b69f \
           file://0001-cmake-Solved-issue-with-nodejs-installation-path.patch \
          "

S = "${WORKDIR}/git"

inherit distutils-base pkgconfig python-dir cmake

PACKAGES =+ "python-${PN} node-${PN} ${PN}-java"

# python-upm package containing Python bindings
FILES_python-${PN} = "${PYTHON_SITEPACKAGES_DIR}/ \
                      ${datadir}/${BPN}/examples/python/ \
                      ${prefix}/src/debug/${BPN}/${PV}-${PR}/build/src/*/pyupm_* \
                     "
RDEPENDS_python-${PN} += "python mraa"
INSANE_SKIP_python-${PN} = "debug-files"

# node-upm package containing Nodejs bindings
FILES_node-${PN} = "${libdir}/node_modules/ \
                    ${datadir}/${BPN}/examples/javascript/ \
                   "
RDEPENDS_node-${PN} += "nodejs mraa"
INSANE_SKIP_node-${PN} = "debug-files"

# upm-java package containing Java bindings
FILES_${PN}-java = "${libdir}/libjava*.so \
                    ${libdir}/java/ \
                    ${datadir}/${BPN}/examples/java/ \
                    ${prefix}/src/debug/${BPN}/${PV}-${PR}/build/src/*/*javaupm_* \
                    ${libdir}/.debug/libjava*.so \
                   "
# include .jar files in /usr/lib/java for 64 bit builds
#FILES_${PN}-java_append = "${@' ${libdir}/../lib/java/*' if '${TARGET_ARCH}' == 'x86_64' else ''}"

RDEPENDS_${PN}-java += "java-runtime mraa-java"
INSANE_SKIP_${PN}-java = "debug-files"


FILES_${PN}-doc += " ${datadir}/upm/examples/"
RDEPENDS_${PN} += " mraa"

PACKAGECONFIG ??= "python nodejs java"
PACKAGECONFIG[python] = "-DBUILDSWIGPYTHON=ON, -DBUILDSWIGPYTHON=OFF, swig-native python,"
PACKAGECONFIG[nodejs] = "-DBUILDSWIGNODE=ON, -DBUILDSWIGNODE=OFF, swig-native nodejs,"
PACKAGECONFIG[java] = "-DBUILDSWIGJAVA=ON, -DBUILDSWIGJAVA=OFF, swig-native icedtea7-native,"

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

