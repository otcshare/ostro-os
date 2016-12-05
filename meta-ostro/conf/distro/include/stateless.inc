INHERIT += "stateless"

###########################################################################

# Temporary overrides until Ostro OS is fully stateless.

# This entry here allows everything in /etc because Ostro OS is
# not actually stateless yet. We merely use the stateless.bbclass
# to remove files from /etc which get written on the device
# and thus must be excluded from images and, more importantly,
# swupd bundles.
STATELESS_ETC_WHITELIST += "*"

# Empty directories must be kept.
STATELESS_ETC_DIR_WHITELIST += "*"

###########################################################################

# As step towards full stateless Ostro OS, we now
# treat some files in /etc as conceptually read-only (i.e. neither
# modified by the OS at runtime nor by an admin). Anything contained
# in the rootfs directories will get bundled and added or updated when
# running "swupd update".
#
# The implication is that we must keep certain files out of the rootfs
# which do get modified at runtime, because otherwise there are
# "swupd verify" failures.

# mtab needs to be a symlink to /proc/mounts, probably forever.
# There is no point in patching that out of binaries, nor is there
# a need to customize it, so the symlink can remain there as read-only
# system component.
STATELESS_ETC_WHITELIST += "mtab"

# OE-core puts some files into /etc which systemd then later overwrites
# unconditionally via /usr/lib/tmpfile.d/etc.conf or creates dynamically
# (machine-id). Therefore we can remove the redundant files from our rootfs
# by not packaging them in the first place.
STATELESS_RM_pn-systemd += " \
    resolv.conf \
"

# machine-id has to be present in images at least as an empty file
# because we might boot with the rootfs read/only. Otherwise
# creating it during early boot fails (see
# systemd/src/core/machine-id-setup.c).
#
# We solve this by keeping it in the rootfs and only excluding it
# from the bundles. Short-term solution, something like this will
# have to be handled by meta-swupd.
STATELESS_ETC_WHITELIST += "machine-id"
# These files must be ignored by swupd.
STATEFUL_FILES += "/etc/machine-id"
SWUPD_FILE_BLACKLIST_append = " ${STATEFUL_FILES}"

# Depend on the installed components and thus has to be computed on
# the device. Handled by systemd during booting or updates.
STATELESS_RM_ROOTFS += " \
    udev/hwdb.bin \
"

# Disable creation of /etc/ld.so.cache in images and bundles. The file
# gets already recreated by systemd anyway when booting. Has to be
# done by unsetting LDCONFIGDEPEND (checked by rootfs.py, which
# creates the ld.so.cache) for all Ostro OS images, but not the
# ostro-initramfs, so we cannot set it unconditionally.
python () {
    if bb.data.inherits_class('ostro-image', d):
        d.setVar('LDCONFIGDEPEND', '')
}
