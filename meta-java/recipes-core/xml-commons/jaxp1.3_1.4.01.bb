DESCRIPTION = "Java XML parser and transformer APIs (DOM, SAX, JAXP, TrAX)"
AUTHOR = "Apache Software Foundation"
LICENSE = "AL2.0 W3C PD"
LIC_FILES_CHKSUM = " \
                    file://LICENSE;md5=d273d63619c9aeaf15cdaf76422c4f87 \
                    file://LICENSE.dom-documentation.txt;md5=31a36539f6ad4bbe3ac3bd45af0de5d3 \
                    file://LICENSE.dom-software.txt;md5=7ffae199ad8b827f8ec8843e35a0591a \
                    file://LICENSE.sac.html;md5=0d5dd06baacb170df81f0079f4b1c7b9 \
                    file://LICENSE.sax.txt;md5=3534555610af53d4b5a8a0d2fb017d35 \
                   "

SRC_URI = "http://archive.apache.org/dist/xml/commons/source/xml-commons-external-${PV}-src.tar.gz;subdir=${BPN}-${PV}"

inherit java-library

DEPENDS = "fastjar-native"

JARFILENAME = "jaxp-1.3.jar"
ALTJARFILENAMES = "xml-apis.jar"

do_compile() {
  mkdir -p build/license
  javac -d build `find javax org -name \*.java`

  cp LICENSE.*.txt README.*.txt build/license

  fastjar -c -m manifest.commons -f ${JARFILENAME} -C build .
}

SRC_URI[md5sum] = "5536f87a816c766f4999ed60593a8701"
SRC_URI[sha256sum] = "8e8a412aeb95644eaf14ec1a5cfd04833e38cac4a01b83d73d7de2368a35a597"

BBCLASSEXTEND = "native"
