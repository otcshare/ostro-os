require openjdk-6-release-6b24.inc

LIC_FILES_CHKSUM = "file://COPYING;md5=59530bdf33659b29e73d4adb9f9f6552"

PR = "${INC_PR}.0"

ICEDTEA = "icedtea6"

SRCREV = "cf80d2049346"
PV = "6b24-1.10.4+1.11-devel+hg${SRCPV}"

ICEDTEA_URI = "hg://icedtea.classpath.org/hg/;module=icedtea6;rev=${SRCREV}"

CACAO_VERSION = "cff92704c4e0"
SRC_URI[cacao.md5sum] = "40b811b8b7f01b51cd21e62255691bc7"
SRC_URI[cacao.sha256sum] = "dc768c9d097fb056ad34fc6d5a57e8fd4f3b24bf515be92acc5ee4208160eb3f"

JAMVM_VERSION = "4617da717ecb05654ea5bb9572338061106a414d"
SRC_URI[jamvm.md5sum] = "740c2587502831cac6797d1233a7e27b"
SRC_URI[jamvm.sha256sum] = "47fce7bd556c1b1d29a93b8c45497e0d872b48b7f535066b303336f29d0f0d8d"

FILESPATH =. "${FILE_DIRNAME}/openjdk-6-6b24:"
