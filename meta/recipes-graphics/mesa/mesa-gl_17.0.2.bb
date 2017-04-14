require mesa_${PV}.bb

SUMMARY += " (OpenGL only, no EGL/GLES)"

FILESEXTRAPATHS =. "${FILE_DIRNAME}/mesa:"

PROVIDES = "virtual/libgl virtual/mesa"

S = "${WORKDIR}/mesa-${PV}"

PACKAGECONFIG ??= "dri ${@bb.utils.filter('DISTRO_FEATURES', 'x11', d)}"

EXCLUDE_FROM_WORLD = "1"
