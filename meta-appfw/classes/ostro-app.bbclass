# This class is for setting variables for application packages.
#
# ostro-app class input variables:
# ------------------------------
#
# OSTRO_USER_NAME:
#       user to create for your app
#
# OSTRO_APP_NAME:
#       name of the application
#
# ostro-app class exported variables:
# ------------------------------
#
# OSTRO_APP_ROOT:
#       path where to install your app
#

inherit useradd

# Tell useradd where the post-install script should go.
USERADD_PACKAGES = "${PN}"

# Set the defaults
OSTRO_USER_SHELL ??= "/sbin/nologin"
OSTRO_USER_APP_NAME ??= "${OSTRO_USER_NAME}-${OSTRO_APP_NAME}"

# Create the user with disallowed login and no extra groups.
USERADD_PARAM_${PN} = "-s ${OSTRO_USER_SHELL} ${OSTRO_USER_APP_NAME}"
GROUPADD_PARAM_${PN} = ""
GROUPMEMS_PARAM_${PN} = ""

OSTRO_APP_DIR ??= "/apps"
OSTRO_APP_ROOT ??= "${OSTRO_APP_DIR}/${OSTRO_USER_NAME}/${OSTRO_APP_NAME}"

export OSTRO_APP_ROOT
RDEPENDS_${PN} += "iot-app-fw"

do_install[postfuncs] += "ostro_app_install"
ostro_app_install () {
    # Move everything outside of OSTRO_APP_DIR into the expected location.
    # At runtime, AppFW will overlay that on top of the normal / directory.
    # Assumes that $OSTRO_APP_DIR already differs at the root level from
    # application files.
    apps_root=$(echo ${OSTRO_APP_DIR} | sed -e 's;//*;/;g' -e 's;^/\([^/]*\);\1;')
    for i in $(ls -1 ${D}); do
        if [ "$i" != $apps_root ]; then
            mv "${D}/$i" "${D}/${OSTRO_APP_ROOT}"
        fi
    done
    for i in $(find "${D}/${OSTRO_APP_ROOT}"); do
        chmod o-rwx $i
    done
}

# Package app files by default.
FILES_${PN} += "${OSTRO_APP_ROOT}"
