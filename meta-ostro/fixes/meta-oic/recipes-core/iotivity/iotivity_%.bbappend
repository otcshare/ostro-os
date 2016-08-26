# openembedded-core now correctly reveals if the build system
# LDFLAGS aren't used (see openembedded-core commit
# a98a8180863ff45b477a1f8439ebcec21151d282).
#
# iotivity is one of the components that does not obey LDFLAGS.
# However, fixing it needs a lot of rework in iotivity's scons
# scripts. 
#
# Temporarily skip "ldflags" for all PACKAGES:
INSANE_SKIP_${PN} += "ldflags"
INSANE_SKIP_${PN}-dev += "ldflags"
INSANE_SKIP_${PN}-tests += "ldflags"
INSANE_SKIP_${PN}-tests-dbg += "ldflags"
INSANE_SKIP_${PN}-plugins += "ldflags"
INSANE_SKIP_${PN}-plugins-dbg += "ldflags"
INSANE_SKIP_${PN}-plugins-samples += "ldflags"
INSANE_SKIP_${PN}-plugins-samples-dbg += "ldflags"
INSANE_SKIP_${PN}-resource += "ldflags"
INSANE_SKIP_${PN}-resource-dev += "ldflags"
INSANE_SKIP_${PN}-resource-thin += "ldflags"
INSANE_SKIP_${PN}-resource-dbg += "ldflags"
INSANE_SKIP_${PN}-resource-samples += "ldflags"
INSANE_SKIP_${PN}-resource-samples-dbg += "ldflags"
INSANE_SKIP_${PN}-resource-thin-staticdev += "ldflags"
INSANE_SKIP_${PN}-service += "ldflags"
INSANE_SKIP_${PN}-service-dbg += "ldflags"
INSANE_SKIP_${PN}-service-staticdev += "ldflags"
INSANE_SKIP_${PN}-service-samples += "ldflags"
INSANE_SKIP_${PN}-service-samples-dbg += "ldflags"
