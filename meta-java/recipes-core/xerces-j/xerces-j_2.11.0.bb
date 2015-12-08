DESCRIPTION = "Reference implementation of XNI, the Xerces Native Interface, and also a fully conforming XML Schema processor."
AUTHOR = "Apache Software Foundation"
LICENSE = "Apache-2.0"

PR = "r1"

LIC_FILES_CHKSUM = " \
                    file://LICENSE;md5=d273d63619c9aeaf15cdaf76422c4f87 \
                    file://LICENSE.DOM-documentation.html;md5=77c27084ca92e9a8efe9314f284acc05 \
                    file://LICENSE.DOM-software.html;md5=1f920675d8473fd5cbabf133a7e39e0d \
                    file://LICENSE.resolver.txt;md5=d229da563da18fe5d58cd95a6467d584 \
                    file://LICENSE.serializer.txt;md5=d229da563da18fe5d58cd95a6467d584 \
                   "

SRC_URI = "http://archive.apache.org/dist/xerces/j/Xerces-J-src.${PV}.tar.gz"

S = "${WORKDIR}/xerces-2_11_0"

inherit java-library java-bootstrap-components

JPN = "libxerces2-java"

DEPENDS = "jaxp1.3 xml-commons-resolver1.1"
DEPENDS_virtclass-native = "jaxp1.3-native xml-commons-resolver1.1-native"

RDEPENDS_${PN} = "libjaxp1.3-java libxml-commons-resolver1.1-java"
RDEPENDS_${PN}_virtclass-native = ""

do_unpackpost() {
  find src -exec \
    sed -i -e "s|@impl.name@|Xerces-J ${PV}|" \
           -e "s|@impl.version@|${PV}|" {} \;
}

addtask unpackpost after do_unpack before do_patch

JARFILENAME = "xercesImpl.jar"
ALTJARFILENAMES = ""

do_compile() {
  mkdir -p build

  # Prepend the bootclasspath with the earlier XML API to make
  # compilation succeed.
  oe_makeclasspath bcp -s jaxp-1.3 resolver
	bcp=$bcp:${STAGING_DATADIR_NATIVE}/classpath/glibj.zip

  javac -sourcepath src -d build -cp $bcp `find src -name "*.java"`

  (cd src && find org ! -name "*.java" -exec cp {} ../build/{} \;)

  fastjar cfm ${JARFILENAME} src/manifest.xerces -C build .

  # Like Debian we provide a symlink called xmlParserAPIs.jar pointing to the JAXP
  # classes.
  ln -sf ${D}${datadir_java}/xmlParserAPIs.jar jaxp-1.3.jar

}

SRC_URI[md5sum] = "d01fc11eacbe43b45681cb85ac112ebf"
SRC_URI[sha256sum] = "f59a5ef7b51bd883f2e9bda37a9360692e6c5e439b98d9b6ac1953e1f98b0680"

BBCLASSEXTEND = "native"
