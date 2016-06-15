# This class is meant to be used in a distro or local conf via
# INHERIT += "supported-recipes".
#
# It automatically excludes unsupported recipes from the world build,
# without having to maintain a set of REMOVE_FROM_WORLD_pn-<recipe>
# entries in an include file.
#
# In addition, there is a pre-build check whether any unsupported
# recipes are required to complete the build. This check is optional,
# see SUPPORTED_RECIPES_CHECK.
#
# Build tools and native recipes are ignored by the class itself.
# Those are considered less important (problems in them cannot be
# exploited on the target platform) and/or they are supported
# by the provider of these tools.

# Space-separated list of filenames of files containing recipe names.
# Content of these files are recipes names, one per line.
# Empty lines and lines starting with a hash are ignored.
SUPPORTED_RECIPES ??= ""

# For each file, the base name is listed in the SUPPORTED_RECIPES_SOURCES
# report under "supported" if the file lists a recipe. This name can
# be substituded with a short and/or nicer name with variable flags.
# The replacement should be a single word with no spaces, as in:
# SUPPORTED_RECIPES[foo-bar-recipe-list.txt] = "foobar".

# Empty skips check, "note/warn/error/fatal" increases the logging level,
# with "fatal" aborting the build.
SUPPORTED_RECIPES_CHECK ??= ""

# Maximum number of dependency chains to print when the check fails.
# Depending on a recipe deep in the stack can produce a lot of output,
# this here acts as safeguard.
SUPPORTED_RECIPES_CHECK_DEPENDENCY_LINES ??= "50"

# This class is written so that it only checks for binaries compiled for
# use on the target device. Helper recipes and toolchain are
# currently excluded from the checking, detected based on certain base
# classes.
#
# The intention is to maintain this as part of this .bbclass, but just
# in case it is done so that users of the class can extend or override
# this logic.
SUPPORTED_RECIPES_NATIVE_BASECLASSES ??= " \
    cross.bbclass \
    cross-canadian.bbclass \
    image.bbclass \
    native.bbclass \
    nativesdk.bbclass \
    packagegroup.bbclass \
    populate_sdk.bbclass \
"

# Show information about all external sources without having to build
# anything. This works also for recipes which do not build (i.e. where
# buildhistory would not work) and it is faster than invoking bitbake -g
# for each recipe (because the meta data only gets loaded once).
#
# Use this by setting the variable to the name of a file and then start a dry run, like this:
# BB_ENV_EXTRAWHITE="$BB_ENV_EXTRAWHITE SUPPORTED_RECIPES_SOURCES" SUPPORTED_RECIPES_SOURCES=/tmp/sources.csv bitbake --dry-run my-build-targets
#
# One can abort after the "NOTE: Created SUPPORTED_RECIPES_SOURCES = <filename>" message.
#
# The output is a comma-separated list of fields:
# - recipe name
# - collection
# - PV
# - HOMEPAGE
# - source
# - SUMMARY
#
# Local files in SRC_URI are ignored. If there is no remaining external source,
# the recipe is not reported. If there is more than one remaining source,
# the first one is considered the "main" source and shown for the original recipe
# name. The remaining ones are show as "recipe name/<name>" where <name> is
# from the "name" parameter in the source URL, or "recipe name/<number>" where
# number counts the non-patch sources.
SUPPORTED_RECIPES_SOURCES ??= ""

# Temporary directory for use with SUPPORTED_RECIPES_SOURCES.
SUPPORTED_RECIPES_SOURCES_DIR ??= "${TMPDIR}/supported-recipe-sources"

# However, not all recipes use these special base classes, so there
# is also this list of space-separated regular expressions which identify
# additional recipes which do not need to be checked.
SUPPORTED_RECIPES_NATIVE_RECIPES ??= " \
    buildtools-tarball \
    depmodwrapper-cross \
    gcc-source-.* \
    glibc-initial \
    libgcc-initial \
    libtool-cross \
    meta-environment-extsdk-.* \
    meta-world-pkgdata \
    nativesdk-buildtools-perl-dummy \
    qemuwrapper-cross \
    shadow-sysroot \
    uninative-tarball \
"

python () {
    import supportedrecipes

    supported_recipes, files = supportedrecipes.load_supported_recipes(d)
    # The bitbake cache must be told explicitly that changes in these
    # files have an effect on the recipe. Otherwise adding
    # or removing entries does not trigger re-parsing and re-building.
    for file in files:
        bb.parse.mark_dependency(d, file)
    if not supported_recipes.current_recipe_supported(d):
        d.setVar('EXCLUDE_FROM_WORLD', '1')
    if d.getVar('SUPPORTED_RECIPES_SOURCES', True):
        supportedrecipes.dump_sources(d)
}

python supported_recipes_eventhandler() {
    import supportedrecipes
    supportedrecipes.check_build(d, e)
}

addhandler supported_recipes_eventhandler
supported_recipes_eventhandler[eventmask] = "bb.event.DepTreeGenerated"
