DESCRIPTION = "Java runtime based upon the OpenJDK- and Icedtea Project"
HOMEPAGE = "http://icedtea.classpath.org"
LICENSE  = "GPL-2.0-with-classpath-exception"
PRIORITY = "optional"
SECTION  = "libs"

ICEDTEA_VERSION = "${@bb.parse.BBHandler.vars_from_file(d.getVar('FILE', False),d)[1].split("-")[1] or '1.0'}"

S = "${WORKDIR}/${ICEDTEA}"

DEPENDS_append_libc-uclibc = " virtual/libiconv "

# The OpenJDK build with interpreter optimizations for ARM depends on a binary
# that generates constants for an assembler source file. There is no other
# way than to generate this on a pseudo machine. Cross-compiling would not help
# because structure sizes and/or alignment may differ.
DEPENDS_append = " qemu-native "

inherit java autotools gettext qemu pkgconfig

B = "${S}/build"

# OpenJDK uses slightly different names for certain arches. We need to know
#	this to create some files which are expected by the build.
def get_jdk_arch(d):
    import bb

    jdk_arch = bb.data.getVar('TRANSLATED_TARGET_ARCH', d, 1)
    if jdk_arch == "x86-64":
        jdk_arch = "amd64"
    elif jdk_arch == "powerpc":
        jdk_arch = "ppc"
    elif jdk_arch == "powerpc64":
        jdk_arch = "ppc64"
    elif (jdk_arch == "i486" or jdk_arch == "i586" or jdk_arch == "i686"):
        jdk_arch = "i386"

    return jdk_arch

JDK_ARCH = "${@get_jdk_arch(d)}"
JDK_HOME = "${libdir_jvm}/${JDK_DIR}"
JDK_FAKE = "${WORKDIR}/fake-jdk"

# A function that is needed in the Shark builds.
def get_llvm_configure_arch(d):
    import bb;

    arch = bb.data.getVar('TRANSLATED_TARGET_ARCH', d, 1)
    if arch == "x86-64" or arch == "i486" or arch == "i586" or arch == "i686":
        arch = "x86"
    elif arch == "arm":
        arch = "arm"
    elif arch == "mipsel" or arch == "mips":
        arch = "mips"
    elif arch == "powerpc" or arch == "powerpc64":
        arch = "powerpc"
    else:
        bb.warn("%s does not support %s yet" % (bb.data.getVar('PN', d, 1), arch) );

    return arch

# Puts an OE specific string into the binary making it possible for the user
# to know where it comes from (and blame the right people ...).
DIST_ID = "Built for ${DISTRO}"
DIST_NAME = "${DISTRO}"
EXTRA_OEMAKE = 'DIST_NAME="${DIST_NAME}" DIST_ID="${DIST_ID}"'

# llvm configure and compiles stuff

export WANT_LLVM_RELEASE = "2.8"

# Provides the target architecture to the configure script.
export LLVM_CONFIGURE_ARCH="${@get_llvm_configure_arch(d)}"

# Large stack is required at least on x86_64 host, otherwise random segfaults appear:
QEMU = "${@qemu_target_binary(d)} ${QEMU_OPTIONS} -s 2097152"

EXTRA_OEMAKE += 'QEMU="${QEMU}"'
