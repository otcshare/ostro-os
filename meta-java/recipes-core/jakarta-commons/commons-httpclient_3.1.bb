require jakarta-commons.inc
LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=369b6d7c5a954dcc3f2e7ac3323507c3"

PR = "${INC_PR}.1"

DESCRIPTION = "Efficient, up-to-date, and feature-rich package implementing the client side of the most recent HTTP standards and recommendations"

SRC_URI = "http://archive.apache.org/dist/httpcomponents/commons-httpclient/source/${BP}-src.tar.gz"

S = "${WORKDIR}/${BP}"

DEPENDS += "commons-logging commons-codec"
RDEPENDS_${PN} = "libcommons-logging-java libcommons-codec-java"

CP = "commons-logging commons-codec"


SRC_URI[md5sum] = "2c9b0f83ed5890af02c0df1c1776f39b"
SRC_URI[sha256sum] = "f9a496d3418b0e15894fb351652cd4fa5ca434ebfc3ce3bb8da40defd8b097f2"
