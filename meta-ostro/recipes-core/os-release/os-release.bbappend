# In Ostro OS We only put mostly static values into the os-release
# package. That avoids unnecessary recompilations.  Dynamic values
# like DISTRO_VERSION (which in our case contain ${DATE}) and BUILD_ID
# (includes ${DATETIME}) get patched to the current values in
# ostro-image.bbclass.

DISTRO_VERSION = "distro-version-to-be-added-during-image-creation"
BUILD_ID = "build-id-to-be-added-during-image-creation"
OS_RELEASE_FIELDS += "BUILD_ID"
