# The "format" needs to be bumped for different reasons:
# - the output of the swupd-server changes in a way that
#   a swupd-client currently installed on devices  will not
#   understand it (example: changing file names or using
#   a new compression method for archives)
# - the content of the distro changes such that a device
#   cannot update directly to the latest build (example:
#   the distro changes the boot loader and some swupd postinst
#   helper which knows about that change must be installed on
#   the device first before actually switching)
#
# meta-swupd handles the first case with SWUPD_TOOLS_FORMAT.
# The default value matches the default versions of the swupd-server
# and swupd-client. Distros can override this if they need to pick
# non-default versions of the tools, but that is not tested.
#
# Distros need to handle the second case by preparing and releasing
# a build that devices can update to (i.e. the version URL the devices
# check must have that update), then make the incompatible change and
# in the next build bump the SWUPD_DISTRO_FORMAT.
#
# In both cases, SWUPD_FORMAT gets bumped. meta-swupd notices that
# and then prepares a special transitional update:
# - the rootfs is configured to use the new SWUUPD_FORMAT and
#   OS_VERSION
# - a fake OS_VERSION-1 release is built using a swupd-server that is
#   compatible with the swupd-client before the bump
# - the OS_VERSION release then is the first one using the new format
#
# This way, devices are forced to update to OS_VERSION-1 because that
# will forever be the "latest" version for their current format.
# Once they have updated, the device really is on OS_VERSION, configured
# to use the new format, and the next update check will see future
# releases again.
#
# For this to work, "swupd-client" should always be invoked without
# explicit format parameter.
SWUPD_TOOLS_FORMAT ?= "4"
SWUPD_DISTRO_FORMAT ?= "0"
SWUPD_FORMAT = "${@ str(int('${SWUPD_TOOLS_FORMAT}') + int('${SWUPD_DISTRO_FORMAT}')) }"


# This version number *must* map to VERSION_ID in /etc/os-release and *must* be
# a non-negative integer that fits in an int.
OS_VERSION ??= "${DISTRO_VERSION}"

python () {
    ver = d.getVar('OS_VERSION', True) or 'invalid'
    try:
        ver = int(ver)
    except ValueError:
        bb.fatal("Invalid value for OS_VERSION (%s), must be a non-negative integer value." % ver)
    if ver <= 0 or ver > 2147483647:
        bb.fatal('OS_VERSION outside of valid range (> 0, <= 2147483647): %d' % ver)
}
