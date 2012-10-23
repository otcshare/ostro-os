DESCRIPTION = "Provides a mean to type data and locate components suitable for performing various kinds of action on it."
AUTHOR = "GNU ClasspathX"
LICENSE = "GPL-2.0-with-GCC-exception"
LIC_FILES_CHKSUM = "file://COPYING;md5=a916467b91076e631dd8edb7424769c7"

PR = "r1"

SRC_URI = "http://ftp.gnu.org/gnu/classpathx/activation-${PV}.tar.gz \
           file://datadir_java.patch \
          "

inherit autotools java-library

S = "${WORKDIR}/activation-${PV}"

export JAVAC = "javac"

# Fake javadoc
export JAVADOC = "true"

JARFILENAME = "activation-${PV}.jar"
ALTJARFILENAMES = "activation.jar gnujaf.jar"

do_compile() {
  mkdir -p build

  javac -sourcepath source -d build `find source -name "*.java"`

  fastjar -C build -c -f ${JARFILENAME} .
}

SRC_URI[md5sum] = "de50d7728e8140eb404f2b4554321f8c"
SRC_URI[sha256sum] = "b1b5ef560d30fcb11fbf537246857d14110ce4eb2b200d4c54690472305d87b7"

BBCLASSEXTEND = "native"

