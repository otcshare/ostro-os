SUMMARY = "Hello world from OTC IoT QA Bundle A"
DESCRIPTION = "test application "
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302" 
SRC_URI = "file://hello-bundle-a.c \
    file://hello-bundle-c.c \
"

S = "${WORKDIR}"
do_compile() {
    ${CC} hello-bundle-a.c -o hello-bundle-a
    ${CC} hello-bundle-c.c -o hello-bundle-c
}
 
do_install() {
    install -d ${D}${bindir}
    install -m 0755 hello-bundle-a ${D}${bindir}
    install -m 0755 hello-bundle-c ${D}${bindir}
}

