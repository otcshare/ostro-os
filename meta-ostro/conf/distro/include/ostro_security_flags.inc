# Include security flags pulled in via openembedded-core.
require conf/distro/include/security_flags.inc

SECURITY_PIC_CFLAGS ?= "-fpic"

# Add Ostro OS specific flags to fix build issues with
# recipes that are being used in Ostro OS.
SECURITY_CFLAGS_pn-zeromq = "${SECURITY_NO_PIE_CFLAGS} ${SECURITY_PIC_CFLAGS}"
SECURITY_CFLAGS_pn-mraa = "${SECURITY_NO_PIE_CFLAGS} ${SECURITY_PIC_CFLAGS}"
SECURITY_CFLAGS_pn-upm = "${SECURITY_NO_PIE_CFLAGS} ${SECURITY_PIC_CFLAGS}"
SECURITY_CFLAGS_pn-iot-app-fw = "${SECURITY_NO_PIE_CFLAGS} ${SECURITY_PIC_CFLAGS}"
SECURITY_CFLAGS_pn-iotivity = "${SECURITY_NO_PIE_CFLAGS} ${SECURITY_PIC_CFLAGS}"
SECURITY_CFLAGS_pn-krb5 = "${SECURITY_NO_PIE_CFLAGS} ${SECURITY_PIC_CFLAGS}"

# openjdk-8 ends up linking with "-shared -pie -fpie" in some cases (see
# hotspot/make/linux/makefiles/saproc.make) which then tries (and fails) to
# produce an executable instead of a shared object because main() is
# undefined.
SECURITY_CFLAGS_pn-openjdk-8 = "${SECURITY_NO_PIE_CFLAGS}"
SECURITY_CFLAGS_pn-openjre-8 = "${SECURITY_NO_PIE_CFLAGS}"

# Additional exceptions for packages in Ostro OS which do not
# compile with -Wformat-security as error (sorted alphabetically).
SECURITY_STRINGFORMAT_pn-dash = ""
SECURITY_STRINGFORMAT_pn-giflib = ""
SECURITY_STRINGFORMAT_pn-gsignond = ""
SECURITY_STRINGFORMAT_pn-openjdk-8 = ""
SECURITY_STRINGFORMAT_pn-openjre-8 = ""
