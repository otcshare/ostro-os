require jakarta-commons.inc
LIC_FILES_CHKSUM = "file://src/java/org/apache/commons/codec/BinaryDecoder.java;endline=15;md5=c08c3e117b4fc42b50c1f621fdcecc5f"

PR = "${INC_PR}.1"

DESCRIPTION = "Java library with simple encoder and decoders for various formats such as Base64 and Hexadecimal"

SRC_URI = "http://archive.apache.org/dist/commons/codec/source/${BP}-src.tar.gz"

S = "${WORKDIR}/${BP}"

SRC_URI[md5sum] = "af3c3acf618de6108d65fcdc92b492e1"
SRC_URI[sha256sum] = "12effcf3fea025bd34edbfec60a6216ca453fb27e781d8e5783caf75fd33d90e"
