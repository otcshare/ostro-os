require jakarta-commons.inc

LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=3b83ef96387f14655fc854ddc3c6bd57"
PR = "${INC_PR}.1"

DESCRIPTION = "A set of abstract data type interfaces and implementations that offer a wealth of useful functionality and a solid foundation for extending that functionality"

SRC_URI = "http://www.apache.org/dist/commons/collections/source/commons-collections-${PV}-src.tar.gz"

S = "${WORKDIR}/commons-collections-${PV}-src"


SRC_URI[md5sum] = "776b51a51312c1854ad8f6d344a47cda"
SRC_URI[sha256sum] = "070d94fe77969d8949bd129a618e6a7bee6b83b5b5db3ef3f983395a5428b914"
