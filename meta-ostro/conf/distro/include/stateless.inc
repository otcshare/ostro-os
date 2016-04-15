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

# As an intermediate step towards full stateless Ostro OS, we now
# treat some files in /etc as conceptually read-only (i.e. neither
# modified by the OS at runtime nor by an admin). Anything contained
# in the rootfs directories will get bundled and added or updated when
# running "swupd update".
#
# The implication is that we must keep certain files out of the rootfs
# which do get modified at runtime, because otherwise there are
# "swupd verify" failures.

# OE-core puts some files into /etc which systemd then later overwrites
# unconditionally via /usr/lib/tmpfile.d/etc.conf or creates dynamically
# (machine-id). Therefore we can remove the redundant files from our rootfs
# by not packaging them in the first place.
#
# Booting without /etc/machine-id triggers the "first boot" condition,
# used for example by systemd-firstboot.service. That service is
# not usable in Ostro OS (depends on user input) and therefore has
# to be disabled when removing machine-id.
STATELESS_RM_pn-base-files += " \
    mtab \
"
STATELESS_RM_pn-systemd += " \
    machine-id \
    resolv.conf \
"

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
