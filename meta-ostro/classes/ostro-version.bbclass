# When building in a CI system with swupd enabled, OS_VERSION must be
# set to a consistent value for all builds. See below
# for an example how that works with Jenkins.
#
# In local builds, we only have ${DATETIME} as something that
# increments automatically, but it is too large for an integer number
# on 32 bit systems. Therefore we substract the 2016 as the initial
# year in which Ostro OS started using swupd and ignore the
# seconds.
#
# The default behavior is to not rebuild just because OS_VERSION
# changed. If that is desired, include in local.conf:
#   VERSION_ID = "${OS_VERSION}"
# This will cause the os-release package to be rebuilt each time
# OS_VERSION changes, and that in turn causes an image and bundle
# rebuild.
#
# For more predictable results is possible to set OS_RELEASE manually,
# either in local.conf or in the environment like this:
#   BB_ENV_EXTRAWHITE="$BB_ENV_EXTRAWHITE OS_VERSION" OS_VERSION=110 bitbake ...

def ostro_get_os_version(d):
    # String operations are used here to remove the last two digits and add back
    # a zero instead of / 100 * 10 because the / operator has different semantic
    # in Python 2 and 3 (integer division vs. floating point division).
    os_version_datetime = str(int(d.getVar('DATETIME', True)) - 20160000000000)[:-2] + '0'
    build_id_str = d.getVar('BUILD_ID', True) or ''
    if build_id_str:
        try:
            build_id = int(build_id_str)
        except ValueError:
            # Assume that BUILD_ID is in CI's format, e.g. "2016-07-10_18-49-16-build-127".
            # We cannot have the definition for OS_VERSION in ostroproject-ci.inc because
            # the file is used also in eSDKs produced by CI where BUILD_ID is not set in
            # the expected format.
            #
            # In the CI system, the integer OS version used for swupd is derived
            # from the Jenkins build number part of the BUILD_ID. The conversion
            # to int and back to string acts as sanity check that we really get a
            # number out of the BUILD_ID.
            #
            # BUILD_ID is expected to have this format:
            # BUILD_ID = "<parent-build-timestamp (of Jenkins top job)>" + "-build-" + "<jenkins-top-job-build-number>"
            #
            # We multiply it by ten, to ensure that the version space has some gap
            # for minor updates. How to actually build minor updates with Jenkins
            # still needs to be determined.
            build_id = int(build_id_str.split('-')[-1]) * 10

        # check if we have reached max value for 32-bit integer
        if build_id > 2147483646:
            bb.warn("The current value for BUILD_ID (%d) doesn't fit 32-bit integer: redefining..." % build_id)
            return os_version_datetime

        return str(build_id)
    else:
        return os_version_datetime

ostro_get_os_version[vardepsexclude] += "DATETIME"

OS_VERSION ?= "${@ostro_get_os_version(d)}"
