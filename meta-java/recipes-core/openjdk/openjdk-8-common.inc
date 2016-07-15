DESCRIPTION = "Java runtime based upon the OpenJDK Project"
HOMEPAGE = "http://http://openjdk.java.net/"
LICENSE  = "GPL-2.0-with-classpath-exception"

LIC_FILES_CHKSUM = "file://LICENSE;md5=7b4baeedfe2d40cb03536573bc2c89b1"

inherit java autotools gettext qemu pkgconfig

AUTOTOOLS_SCRIPT_PATH = "${S}/common/autoconf/"
export AUTOCONF_DIR="${AUTOTOOLS_SCRIPT_PATH}"

FILESPATH =. "${FILE_DIRNAME}/patches-openjdk-8:"

# for weird openjdk-common.inc
S = "${WORKDIR}/${OPENJDK_HG_U}-${OPENJDK_CHANGESET}"

SRC_URI = " \
    ${OPENJDK_URI} \
    ${HOTSPOT_URI} \
    ${CORBA_URI} \
    ${JAXP_URI} \
    ${JAXWS_URI} \
    ${JDK_URI} \
    ${LANGTOOLS_URI} \
    ${NASHORN_URI} \
    file://LICENSE \
    ${PATCHES_URI} \
"

do_unpack_extract_submodules () {
    cd "${S}"
    # tar --transform
    tar xjf ${WORKDIR}/${CORBA_FILE} --transform "s,-${CORBA_CHANGESET},,g"
    tar xjf ${WORKDIR}/${HOTSPOT_FILE} --transform "s,-${HOTSPOT_CHANGESET},,g"
    tar xjf ${WORKDIR}/${JAXP_FILE} --transform "s,-${JAXP_CHANGESET},,g"
    tar xjf ${WORKDIR}/${JAXWS_FILE} --transform "s,-${JAXWS_CHANGESET},,g"
    tar xjf ${WORKDIR}/${JDK_FILE} --transform "s,-${JDK_CHANGESET},,g"
    tar xjf ${WORKDIR}/${LANGTOOLS_FILE} --transform "s,-${LANGTOOLS_CHANGESET},,g"
    tar xjf ${WORKDIR}/${NASHORN_FILE} --transform "s,-${NASHORN_CHANGESET},,g"
}

def package_config_option_cleanup(d):
    distro_x11 = bb.utils.contains('DISTRO_FEATURES', 'x11', True, False, d)
    distro_alsa = bb.utils.contains('DISTRO_FEATURES', 'alsa', True, False, d)
    distro_pulseaudio = bb.utils.contains('DISTRO_FEATURES', 'pulseaudio', True, False, d)

    with_x11 = bb.utils.contains('PACKAGECONFIG', 'x11', True, False, d)
    with_cups = bb.utils.contains('PACKAGECONFIG', 'cups', True, False, d)
    with_alsa = bb.utils.contains('PACKAGECONFIG', 'alsa', True, False, d)
    with_pulseaudio = bb.utils.contains('PACKAGECONFIG', 'pulseaudio', True, False, d)

    option_headless = bb.utils.contains('PACKAGECONFIG', 'headless', True, False, d)
    option_headful = bb.utils.contains('PACKAGECONFIG', 'headful', True, False, d)
    option_soundless = bb.utils.contains('PACKAGECONFIG', 'soundless', True, False, d)

    if option_headless and option_headful:
        option_headless = False

    if option_headful and not with_x11:
        with_x11 = True

    if option_headful and not with_cups:
        with_cups = True

    if option_soundless and with_alsa:
        with_alsa = False

    if option_soundless and with_pulseaudio:
        with_pulseaudio = False

    if with_x11 and not distro_x11:
        with_x11 = False

    if with_alsa and not distro_alsa:
        with_alsa = False

    if with_pulseaudio and not distro_pulseaudio:
        with_pulseaudio = False

    if option_headful and not with_x11:
        option_headful = False

    if option_headful and not with_cups:
        option_headful = False

    if not option_headless and not with_x11:
        option_headless = True

    if not option_headless and not with_cups:
        option_headless = True

    if not option_soundless and not with_alsa:
        option_soundless = True

    if not option_soundless and not with_pulseaudio:
        option_soundless = True

    options = {'make': [], 'cpp': [], 'env': [], 'configure': ["--disable-ccache"] }

    if option_headful:
        options['configure'].append("--enable-headful")

    if option_headless:
        options['configure'].append("--disable-headful")
        options['make'].append("BUILD_HEADLESS_ONLY=1")
        options['make'].append("BUILD_HEADLESS=true")
        options['cpp'].append("-DHEADLESS=true")

    if option_soundless:
        options['make'].append("BUILD_SOUNDLESS_ONLY=1")

    if not with_x11:
        options['make'].append("X11_NOT_NEEDED=1")
        options['env'].append("X11_NOT_NEEDED=yes")

    if not with_cups:
        options['make'].append("CUPS_NOT_NEEDED=1")
        options['env'].append("CUPS_NOT_NEEDED=yes")

    if not with_alsa:
        options['make'].append("ALSA_NOT_NEEDED=1")
        options['env'].append("ALSA_NOT_NEEDED=yes")

    if not with_pulseaudio:
        options['make'].append("PULSE_NOT_NEEDED=1")
        options['env'].append("PULSE_NOT_NEEDED=yes")

    options = [ ' '.join(options['make']), ' '.join(options['cpp']), ' '.join(options['env']), ' '.join(options['configure']) ]

    return options

def jdk_make_options(d):
    options = package_config_option_cleanup(d)
    return options[0]

def jdk_cpp_options(d):
    options = package_config_option_cleanup(d)
    if not options[1]:
        return ""

    return " " + options[1]

def jdk_environment_options(d):
    options = package_config_option_cleanup(d)
    return options[2]

def jdk_configure_options(d):
    options = package_config_option_cleanup(d)
    return options[3]

do_unpack[postfuncs] += "do_unpack_extract_submodules"

POST_CONFIGURE_CLEAN_X11 = "${@bb.utils.contains('PACKAGECONFIG', 'x11', '', 'rm -f jdk/src/solaris/classes/sun/awt/X11/*.java', d)}"

do_patch_openjdk8() {
        olddir=`pwd`
        cd "${S}"
        ${POST_CONFIGURE_CLEAN_X11}
        for OJ8P in ${WORKDIR}/openjdk8-*.patch; do
                patch -p0 < ${OJ8P}
        done
}

do_patch[postfuncs] += "do_patch_openjdk8"

do_configure_prepend() {
        export ${@jdk_environment_options(d)}
}

# OpenJDK supports parallel compilation but uses a plain number for this.
# In OE we have PARALLEL_MAKE which is the actual option passed to make,
# e.g. "-j 4".
OPENJDK8_PARALLEL_MAKE := "${PARALLEL_MAKE}"
PARALLEL_MAKE = ""
def get_jdk8_native_jobs(d):
    import bb

    pm = bb.data.getVar('OPENJDK8_PARALLEL_MAKE', d, 1);
    if not pm:
        return "1"

    pm = pm.split("j");
    if (len(pm) == 2):
        return pm[1].strip()

    # Whatever found in PARALLEL_MAKE was not suitable.
    return "1"

get_jdk8_native_jobs[vardepsexclude] += "OPENJDK8_PARALLEL_MAKE"

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

# Provides the target architecture to the configure script.
export LLVM_CONFIGURE_ARCH="${@get_llvm_configure_arch(d)}"

# OpenJDK uses slightly different names for certain arches. We need to know
# this to create some files which are expected by the build.
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

export DEBUG_BINARIES = "true"

ALTERNATIVE_PRIORITY = "50"

OPENJDK_UPDATE_VERSION = "${@bb.data.getVar('PV', d, 1).split('b')[0]}"
OPENJDK_BUILD_NUMBER = "b${@bb.data.getVar('PV', d, 1).split('b')[1]}"
EXTRA_OECONF_append = "\
        --with-build-number=${OPENJDK_BUILD_NUMBER} \
        --with-update-version=${OPENJDK_UPDATE_VERSION} \
"

# GCC 6 sets the default C++ standard to C++14 and introduces dead store
# elimination by default. OpenJDK 8 is not ready for either of these
# changes.
FLAGS_GCC6 = "-fno-lifetime-dse -fno-delete-null-pointer-checks"

# All supported cross compilers support the compiler flags that were
# added to make compilation with gcc6 work. But the host compiler for
# native compilation is a different story: it may be too old (for example,
# gcc 4.9.2 on Debian Wheezy). In that case we need to check what the
# version is and only add the flags that are appropriate for that GCC
# version.

def version_specific_cflags(d):
    extraflags = None
    version = None

    if bb.data.inherits_class('native', d):
        from subprocess import Popen, PIPE

        cmd = d.expand('${CPP} -P -').split()
        cc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        # This check is GCC specific. Clang always returns 4. For Clang
        # __clang_major__ and __clang_minor__ need to be checked. Ideally
        # __GNUC_MINOR__ would be checked as well, but for this recipe
        # GCC major is all we care about.
        version = cc.communicate(b'__GNUC__')[0].decode('utf-8')[0]
    else:
        # in the cross case, trust that GCCVERSION is correct. This won't
        # work if the native toolchain is Clang, but as of this writing that
        # doesn't work anyway.
        version = d.getVar('GCCVERSION', expand=True)[0]

    if int(version) >= 4:
        extraflags = d.getVar('FLAGS_GCC%d' % int(version), True)

    return ''.join(extraflags)

CFLAGS_append = " ${@version_specific_cflags(d)}"
CXXFLAGS_append = " ${@version_specific_cflags(d)}"
CXX_append = " -std=gnu++98"
