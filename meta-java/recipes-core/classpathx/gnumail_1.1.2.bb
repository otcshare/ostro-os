DESCRIPTION = "GNU's free implementation of the JavaMail API specification"
AUTHOR = "GNU ClasspathX"
LICENSE = "GPL+libraryexception"
LIC_FILES_CHKSUM = "file://COPYING;md5=14bc6ee8b2e2b409be599212867d126e"

SRC_URI = "http://ftp.gnu.org/gnu/classpathx/mail-${PV}.tar.gz \
           file://datadir_java.patch \
          "

inherit java-library autotools

S = "${WORKDIR}/mail-${PV}"

DEPENDS = "gnujaf inetlib"
DEPENDS_virtclass-native = "gnujaf-native inetlib-native"

export JAVAC = "${STAGING_BINDIR_NATIVE}/javac"
export JAVA = "${STAGING_BINDIR_NATIVE}/java"

# Fake javadoc
export JAVADOC = "true"

EXTRA_OECONF = " \
                --with-inetlib-jar=${STAGING_DATADIR_JAVA} \
                --with-activation-jar=${STAGING_DATADIR_JAVA} \
               "

do_compile() {
  oe_runmake \
    JARDIR=${datadir_java} \
    gnumail_jar=${JARFILENAME} \
    providers_jar=${P}-providers.jar
}

SRC_URI[md5sum] = "0a94ff4328ceb6a4131be96946976a33"
SRC_URI[sha256sum] = "5eb09597a8f81bfc943206e3e0f45b963ba605a646051c353374f1b475bb9f04"

BBCLASSEXTEND = "native"

