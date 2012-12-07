DESCRIPTION = "Java library to help the programmer output log statements to a variety of output targets"
AUTHOR = "Apache Software Foundation"
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=f4ce41a6d1028498fcacde12f589bce7"

PR = "r2"

SRC_URI = "http://archive.apache.org/dist/logging/log4j/${PV}/log4j-${PV}.tar.gz"

inherit java-library

DEPENDS = "gnumail gnujaf"
DEPENDS_virtclass-native = "gnumail-native gnujaf-native"

S = "${WORKDIR}/apache-log4j-${PV}"

JARFILENAME = "log4j-${PV}.jar"
ALTJARFILENAMES = "log4j-1.2.jar log4j1.2.jar"

do_compile() {
  mkdir -p build

  oe_makeclasspath cp -s activation gnumail gnujaf

  # Built everything but the JMS and JMX classes (like in Debian)
	javac -sourcepath src/main/java -cp $cp -d build `find src/main/java -name "*.java" -and -not \( -iwholename "*jms*" -or -iwholename "*jmx*" \)`

  cp -R src/main/resources/* build/

  fastjar -C build -c -f ${JARFILENAME} .
}

SRC_URI[md5sum] = "8218714e41ee0c6509dcfeafa2e1f53f"
SRC_URI[sha256sum] = "a528e3771ee6234661b5eb0fa02e14faee89dfec38de94088c163ddf2a0a8663"

BBCLASSEXTEND = "native"

