# ECJ as a bootstrap compiler is a drop-in replacement for Sun's javac. It offers no more
# and no less features.
#
# This recipe uses the jar created by libecj-bootstrap.

DESCRIPTION = "JDT Core Batch Compiler - Bootstrap variant"
HOMEPAGE = "http://www.eclipse.org/"
SECTION = "devel"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COREBASE}/LICENSE;md5=4d92cd373abda3937c2bc47fbc49d690 \
                    file://${COREBASE}/meta/COPYING.MIT;md5=3da9cfbcb788c80a0384361b4de20420 \
                   "
PR = "r1"

DEPENDS = "libecj-bootstrap virtual/java-native"

PROVIDES = "virtual/javac-native"

SRC_URI = "file://ecj.in"

S = "${WORKDIR}"

JAR = "ecj-bootstrap.jar"

inherit native

do_compile() {
  # Create the start script
  echo "#!/bin/sh" > ecj-bootstrap
  echo "ECJ_JAR=${STAGING_DATADIR}/java/${JAR}" >> ecj-bootstrap
  echo "RUNTIME=java" >> ecj-bootstrap
  cat ecj.in >> ecj-bootstrap
}

do_install() {
  install -d ${D}${bindir}
  install -m 755 ${S}/ecj-bootstrap ${D}${bindir}
  install -m 755 ${S}/ecj-bootstrap ${D}${bindir}/javac
}
