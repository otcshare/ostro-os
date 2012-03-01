require openjdk-6-release-6b24.inc

LIC_FILES_CHKSUM = "file://COPYING;md5=59530bdf33659b29e73d4adb9f9f6552"

PR = "${INC_PR}.0"

ICEDTEA = "icedtea6"

SRCREV = "54ceda20a02c"
PV = "6b24-1.11.1+1.11.2-devel+hg${SRCPV}"

ICEDTEA_URI = "hg://icedtea.classpath.org/hg/;module=icedtea6;rev=${SRCREV}"
