# openembedded-core now correctly reveals if the build system
# LDFLAGS aren't used (see openembedded-core commit
# a98a8180863ff45b477a1f8439ebcec21151d282).
#
# iotivity-simple-client is one of the components that does not obey LDFLAGS.
#
# Temporarily skip "ldflags" to overcome the issue.
INSANE_SKIP_${PN} += "ldflags"
