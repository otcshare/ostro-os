SUMMARY = "Tools expected in an interactive shell"
DESCRIPTION = "Tools listed here are meant to be useful when logged into a device \
and working in the shell interactively or with some custom scripts. In production \
images without shell access they are optional. Tools with a specific purpose like \
development, profiling or program debugging are listed in separate package groups. \
"
LICENSE = "MIT"

inherit packagegroup

RDEPENDS_${PN} = " \
    atop \
    curl \
    gawk \
    htop \
    iftop \
    iotop \
    iputils-arping \
    iputils-clockdiff \
    iputils-ping \
    iputils-ping6 \
    iputils-tracepath \
    iputils-tracepath6 \
    iputils-traceroute6 \
    procps \
    rsync \
    traceroute \
    vim \
    wget \
"
