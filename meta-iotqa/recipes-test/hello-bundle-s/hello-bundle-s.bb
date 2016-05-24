SUMMARY = "Hello world from OTC IoT QA Bundle S"
DESCRIPTION = "test application "
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302" 
SRC_URI = "file://hello-bundle-s.c \
"

S = "${WORKDIR}"
do_compile() {
    ${CC} hello-bundle-s.c -o hello-bundle-s
}
 
do_install() {
    install -d ${D}${bindir}
    install -m 0755 hello-bundle-s ${D}${bindir}
}

