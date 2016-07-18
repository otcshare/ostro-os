# Recent bluez5 releases started limiting the capabilities of
# bluetoothd. When running on a Smack-enabled system, that change has the
# effect that bluetoothd can no longer create the input device under
# /sys because bluez5 running with label "System" has no write
# access to that.
#
# It works when running as normal root with unrestricted capabilities
# because then CAP_MAC_OVERRIDE (a Smack-specific capability) allows
# the process to ignore Smack rules.
#
# We need to ensure that bluetoothd still has that capability.
#
# To fix the issue, Patick and Casey(the Smack architect) had a talk
# about it in Ostro dev mail list. Casey has some ideas about the issue:
# "Turning off privilege is a great thing to do *so long as you don't
# really need the privilege*. In this case you really need it.
# The application package isn't written to account for Smack's use of
# CAP_MAC_OVERRIDE as the mechanism for controlling this dangerous operation.
# Yes, it would be possible to change /proc to change the Smack label on
# that particular file, but that might open other paths for exploit.
# I say give the program the required capability. The program maintainer
# may well say change the kernel handling of /proc. You're stuck in the
# middle, as both work the way they're intended and hence the system
# doesn't work. :( There isn't a way to make this work without "loosening"
# something."
# Therefore, when we we run the program with CAP_MAC_OVERRIDE,
# the whole reason for having capabilities is so the we can give a
# process the ability to bypass one kind of check without giving it the
# ability to bypass other, unrelated checks. A process with
# CAP_MAC_OVERRIDE is still constrained by the file mode bits.
# We was overly worried about granting that capability.
# When it has no other effect than excluding a process from Smack MAC enforcement,
# then adding to the process seems like the right solution for now.
#
# The conclusion from Patick and Casey is that the Smack architect give the key point
# that this is the solution preferred.
#
# Because the solution is to some extend specific to the environment
# in which connmand runs, this change is not submitted upstream
# and it can be overridden by a distro via FIX_BLUEZ5_CAPABILITIES.
#
# The related patch has been submitted to upstream too.
# upstream link: http://permalink.gmane.org/gmane.linux.bluez.kernel/67993

FIX_BLUEZ5_CAPABILITIES ??= ""
FIX_BLUEZ5_CAPABILITIES_smack ??= "fix_bluez5_capabilities"
do_install[postfuncs] += "${FIX_BLUEZ5_CAPABILITIES}"

fix_bluez5_capabilities () {
    service="${D}/${systemd_unitdir}/system/bluetooth.service"
    if [ -f "$service" ] &&
        grep -q '^CapabilityBoundingSet=' "$service"; then
        sed -i -e 's/^CapabilityBoundingSet=/CapabilityBoundingSet=CAP_MAC_OVERRIDE /' "$service"
    fi
}
