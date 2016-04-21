# ECJ as a bootstrap compiler is a drop-in replacement for Sun's javac. It offers no more
# and no less features.

# This variant runs on the initial (not Java5-compatible runtime).

DESCRIPTION = "JDT Core Batch Compiler - Bootstrap variant"
HOMEPAGE = "http://www.eclipse.org/"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

DEPENDS = "libecj-bootstrap-native"

SRC_URI = "file://ecj-initial.in"

S = "${WORKDIR}"

inherit native

JAR = "ecj-bootstrap.jar"

do_compile() {
  # Create the start script
  echo "#!/bin/sh" > ecj-initial

  # get absolute path to parent directory, and use that as base path for the jar
  echo "SH_DIR=\`dirname "\$0"\`" >> ecj-initial
  echo "CURRENT_DIR=\`cd "\${SH_DIR}" && pwd\`" >> ecj-initial
  echo "PARENT_DIR=\`dirname \${CURRENT_DIR}\`" >> ecj-initial

  echo "ECJ_JAR=\${PARENT_DIR}/share/java/${JAR}" >> ecj-initial
  echo "RUNTIME=java-initial" >> ecj-initial
  cat ecj-initial.in >> ecj-initial
}


do_install() {
  install -d ${D}${bindir}
  install -m 755 ${S}/ecj-initial ${D}${bindir}
}
