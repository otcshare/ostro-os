DESCRIPTION = "Library to resolve various public or system identifiers into accessible URLs (Java)"
AUTHOR = "Apache Software Foundation"
LICENSE = "Apache-2.0"
PR = "r1"
LIC_FILES_CHKSUM = "file://LICENSE.resolver.txt;md5=d229da563da18fe5d58cd95a6467d584"

SRC_URI = "http://archive.apache.org/dist/xml/commons/xml-commons-resolver-${PV}.tar.gz"

inherit java-library java-bootstrap-components

S = "${WORKDIR}/xml-commons-resolver-${PV}"

DEPENDS = "jaxp1.3"
DEPENDS_virtclass-native = "jaxp1.3-native"

do_unpackpost() {
  find src -exec \
    sed -i -e "s|@impl.name@|XmlResolver|" \
           -e "s|@impl.version@|1.2|" {} \;
}

addtask unpackpost after do_unpack before do_patch

JARFILENAME = "resolver.jar"
ALTJARFILENAMES = ""

do_compile() {
  mkdir -p build

  cp=${STAGING_DATADIR_JAVA}/jaxp1.3.jar

  javac -sourcepath src -d build -classpath $cp `find src -name "*.java" -and -not  -wholename "*tests*"`

  (cd src && find org -name "*.xml" -o -name "*.txt" -o -name "*.src" -exec cp {} ../build/{} \;)

  fastjar cfm ${JARFILENAME} src/manifest.resolver -C build  org
}

SRC_URI[md5sum] = "46d52acdb67ba60f0156043f30108766"
SRC_URI[sha256sum] = "55dbe7bd56452c175320ce9a97b752252c5537427221323c72e9b9c1ac221efe"

BBCLASSEXTEND = "native"
