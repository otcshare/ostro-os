DESCRIPTION = "Another Neat Tool - build system for Java"
AUTHOR = "Apache Software Foundation"
HOMEPAGE = "http://ant.apache.org"
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=503bb72c4dd62dd216d6820d5b869442"
PR = "r1"

SRC_URI = "http://archive.apache.org/dist/ant/source/apache-ant-${PV}-src.tar.gz \
	   file://ant \
	  "

S = "${WORKDIR}/apache-ant-${PV}"

inherit java-library java-native

DEPENDS = " \
	jsch-native bsf-native xalan-j-native xerces-j-native \
	xml-commons-resolver1.1-native gnumail-native gnujaf-native \
	bcel-native regexp-native log4j1.2-native antlr-native oro-native \
	junit-native jdepend-native commons-net-native commons-logging-native \
	"

do_removecruft() {
	# Removes thing that need proprietary Jar files or are otherwise problematic
	rm -rf ${S}/src/main/org/apache/tools/ant/taskdefs/optional/image
	rm -rf ${S}/src/main/org/apache/tools/ant/types/optional/image
	rm -rf ${S}/src/main/org/apache/tools/ant/taskdefs/optional/ejb
	rm -rf ${S}/src/main/org/apache/tools/ant/taskdefs/optional/scm
	rm -rf ${S}/src/main/org/apache/tools/ant/taskdefs/optional/starteam
	rm -rf ${S}/src/main/org/apache/tools/ant/taskdefs/optional/NetRexxC.java
}

addtask removecruft before do_patch after do_unpack

do_compile() {
  mkdir -p build

  oe_makeclasspath cp -s jsch bsf xalan2 xercesImpl resolver gnumail gnujaf bcel regexp log4j1.2 antlr oro junit jdepend commons-net commons-logging
  cp=build:$cp

  find src/main -name "*.java" > java_files

  javac -sourcepath src/main -cp $cp -d build @java_files

  mkdir -p build/org/apache/tools/ant/types/conditions

  cp -r src/resources/org build/
  (cd src/main && find . \( -name "*.properties" -or -name "*.xml" -or -name "*.mf" \) -exec cp {} ../../build/{} \;)

  echo "VERSION=${PV}" > build/org/apache/tools/ant/version.txt
  echo "DATE=`date -R`" >> build/org/apache/tools/ant/version.txt

  fastjar -C build -c -f ${JARFILENAME} .

  oe_makeclasspath cp -s ecj-bootstrap jsch bsf xalan2 xercesImpl resolver gnumail gnujaf bcel regexp log4j1.2 antlr oro junit jdepend commons-net commons-logging
  cp=${STAGING_DATADIR_JAVA_NATIVE}/ant.jar:${STAGING_DATADIR}/classpath/tools.zip:$cp
  sed -i -e"s|@JAR_FILE@|$cp|" ${WORKDIR}/ant
}

do_install_append() {
	install -d ${D}${bindir}
	install -m 0755 ${WORKDIR}/ant ${D}${bindir}
}

SRC_URI[md5sum] = "9e5960bd586d9425c46199cdd20a6fbc"
SRC_URI[sha256sum] = "4f39057af228663c3cfb6dcfbee603a071a7e3cf48c95c30869ed81c5fcf21c8"

