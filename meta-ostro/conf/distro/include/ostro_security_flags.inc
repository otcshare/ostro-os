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

# Add format string-specific flags
SECURITY_CFLAGS += "-Wformat -Wformat-security"
SECURITY_NO_PIE_CFLAGS += "-Wformat -Wformat-security"

# these packages do not compile with Wformat and Wformat-security
SECURITY_CFLAGS_remove_pn-openjdk-8 = "-Wformat -Wformat-security"
SECURITY_CFLAGS_remove_pn-openjre-8 = "-Wformat -Wformat-security"
SECURITY_CFLAGS_remove_pn-gsignond = "-Wformat -Wformat-security"
SECURITY_CFLAGS_remove_pn-soletta-dev-app = "-Wformat -Wformat-security"
