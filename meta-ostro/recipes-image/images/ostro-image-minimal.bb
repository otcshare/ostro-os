SUMMARY = "Ostro base image."
DESCRIPTION = "Ostro image for local builds with swupd disabled and no optional components whatsoever. The expected usage is to copy this recipe into a custom layer under a different name and then modifying it there to define the image for an Ostro OS based product."

# In normal images without swupd it is possible to set per-image
# variables for a specific image recipe using the the _pn-<image name>
# notation.  However, that stops working once the swupd feature gets
# enabled (because that internally relies on virtual images under
# different names), so the recommended approach is to have per-recipe
# variables (like OSTRO_IMAGE_MINIMAL_EXTRA_FEATURES) and customize
# those outside the recipe.
#
# When copying the recipe, change the OSTRO_IMAGE_MINIMAL prefix
# so that it matches the renamed recipe.
OSTRO_IMAGE_MINIMAL_EXTRA_FEATURES ?= ""
OSTRO_IMAGE_MINIMAL_EXTRA_INSTALL ?= ""
OSTRO_IMAGE_EXTRA_FEATURES += "${OSTRO_IMAGE_MINIMAL_EXTRA_FEATURES}"
OSTRO_IMAGE_EXTRA_INSTALL += "${OSTRO_IMAGE_MINIMAL_EXTRA_INSTALL}"

inherit ostro-image
