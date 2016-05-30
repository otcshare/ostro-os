#
# https://ostroproject.org/jenkins CI configuration:
# This file applied via conf/auto.conf for every build
# happening in Ostro Project CI
#

#
# Static section
# Items that are always present in any CI build:
#

# Generate summary statistics
INHERIT += "buildstats-summary"

# Enable CVE and other security checks.
INHERIT += "isafw"

# Most of the images are expected to contain GPLv3
# components. Therefore we only enable the license check for those
# which must not have them (whitelisting), instead of excluding images
# from the check (blacklisting).
ISAFW_LA_PLUGIN_IMAGE_WHITELIST = "ostro-image-minimal ostro-initramfs"

# ostro-image-minimal is only getting built below as proof that an Ostro OS root
# filesystem is possible without depending on GPLv3 components. The actual
# image files are not needed for that.
IMAGE_FSTYPES_pn-ostro-image-minimal = ""
OSTRO_VM_IMAGE_TYPES_pn-ostro-image-minimal = ""

# Enable extended buildhistory:
INHERIT += "buildhistory"
BUILDHISTORY_COMMIT = "1"
INHERIT += "buildhistory-extra"

# Test data generation:
INHERIT += "test-iot"
TEST_EXPORT_DIR = "iottest"
TEST_TARGET = "simpleremote"

# SDK defaults:
SDKMACHINE ?= "x86_64"

# Generate source mirror tarballs:
BB_GENERATE_MIRROR_TARBALLS = "1"

# Configure images in "development mode".
require conf/distro/include/ostro-os-development.inc

# XXX Drop the VM hack after taking care also of the non UEFI devices
# (those using U-Boot: edison and beaglebone)
OSTRO_VM_IMAGE_TYPES = "dsk.xz dsk.zip dsk.ova dsk.bmap dsk.xz.sha256sum"

#
# Automated build targets
# Those targets should be space separated list of items,
# which must contain only alphanumeric symbols,'-' and '_'.
# Any other symbols would be skipped in parser.
#
# Following targets would be used to perform default build task:
OSTROPROJECT_CI_BUILD_TARGETS="ostro-image-noswupd ostro-image-swupd ostro-image-swupd-dev ostro-image-minimal"
# Following targets would be executed with do_populate_sdk task
OSTROPROJECT_CI_SDK_TARGETS=""
# Following targets would be executed with do_populate_sdk_ext task.
# Uses the fully-populated image to ensure that the eSDK is as complete
# as possible.
OSTROPROJECT_CI_ESDK_TARGETS="ostro-image-swupd-all"
# Following targets would be executed with do_test_iot_export task
OSTROPROJECT_CI_TEST_EXPORT_TARGETS="ostro-image-swupd-dev"
# Execute automatic tests for following images with corresponding
# test suite and test files.
# Space separated list of tuples, each should in format:
# <image_name>,<testsuite_name>,<testfiles_name>,$MACHINE
OSTROPROJECT_CI_TEST_RUNS="ostro-image-swupd-dev,iot-testsuite.tar.gz,iot-testfiles.${MACHINE}.tar.gz,${MACHINE}"

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
OS_VERSION ?= "${@ str(int('${BUILD_ID}'.split('-')[-1]) * 10) }"

#
# Dymamic section.
# Values are applied dynamically based on runtime config or builder host
# parameters.
# Present here as reference only.
#

# Explicit machine declaration by build job:
# MACHINE = "$TARGET_MACHINE"

# Shared download directory between builders:
# DL_DIR = "/srv/bb-cache/ostro-os/sources"

# Limit CPU utilization, based on amount of slots/CPU cores
# on builder hosts:
# BB_NUMBER_PARSE_THREADS = "X"
# BB_NUMBER_THREADS = "X"
# PARALLEL_MAKE = "-j X"

# Local optimizations on SSTATE directories, shared between builder hosts:
# SSTATE_MIRRORS ?= "file://.* http://$IP/bb-cache/ostro-os/sstate/PATH"
# SSTATE_DIR ?= "/var/tmp/sstate-$slot"

# Local directory, where builder puts local copy of buildhistory
# BUILDHISTORY_DIR ?="$WORKSPACE/buildhistory"

# PRserv host dynamically allocated by master:
# PRSERV_HOST = "$IP:$PORT"

# Enabled for master release builds:
# INHERIT += "archiver"
# ARCHIVER_MODE[src] = "original"
# ARCHIVER_MODE[diff] = "1"
# ARCHIVER_MODE[recipe] = "1"
