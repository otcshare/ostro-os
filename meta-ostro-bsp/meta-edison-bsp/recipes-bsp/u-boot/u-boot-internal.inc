PV = "2014.04-1"
S = "${WORKDIR}/git"

PACKAGE_ARCH = "${MACHINE_ARCH}"

SRC_URI = "git://github.com/01org/edison-u-boot.git;branch=edison-v2014.04;protocol=git" 
SRC_URI += "${@'file://${MACHINE}.env' if '${MACHINE}' in ('edison',) else ''}"
SRC_URI += "file://target_env/;name=target-env"
SRC_URI += "file://0001-Backport-compiler-gcc.h-from-4.2-kernel.patch"
SRC_URI += "file://0002-Fix-weak-external-function-references-for-gcc5.patch"
SRC_URI += "file://0001-Fix-missing-stdint.h-include.patch"
SRCREV = "e4177b9f38f41f55eac05c7c1c9275d10653aa1b"
