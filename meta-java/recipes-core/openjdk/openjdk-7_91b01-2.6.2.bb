require openjdk-7-common.inc

LIC_FILES_CHKSUM = "file://COPYING;md5=59530bdf33659b29e73d4adb9f9f6552"

FILESPATH =. "${FILE_DIRNAME}/patches-openjdk-7:"

inherit distro_features_check

REQUIRED_DISTRO_FEATURES = "x11"

PR = "${INC_PR}.1"

SRC_URI[iced.md5sum] = "a16b3e800030db9d9b35f80dfd11883a"
SRC_URI[iced.sha256sum] = "c19eafacd23c81179934acab123511c424cd07c094739fa33778bf7cc80e14d0"

SRC_URI[corba.md5sum] = "500547dc50acde20fad18d0645be89c4"
SRC_URI[corba.sha256sum] = "92fa1e73dc0eb463bccd9ce3636643f492b8935cb7a23b91c5d855f4641382af"

SRC_URI[jaxp.md5sum] = "793fb78b5f51323e31785bb89292182f"
SRC_URI[jaxp.sha256sum] = "94cda3ba29ab3cd36d50f2e6c98a5e250eb6372379e171288b3022b978136fc0"

SRC_URI[jaxws.md5sum] = "131e2f619455e37cea74ca710e6ada6d"
SRC_URI[jaxws.sha256sum] = "14467736097197a199b483f24f8111e9c76252a2ad2a5f166c97585c0a3930d4"

SRC_URI[jdk.md5sum] = "6e8061b2b7c22163ab149fb66553eda8"
SRC_URI[jdk.sha256sum] = "7ad801d5f6b61818c78f2f39931df24d8c6f6a1c821180c998975ac884eb8af1"

SRC_URI[langtools.md5sum] = "1cebffc6b56e9efdbe08eff018801cb1"
SRC_URI[langtools.sha256sum] = "a53fe8912b8190d82615778cf8bfb77202a55adcdc5bacc56ce7738b6a654335"

SRC_URI[openjdk.md5sum] = "d63c5b401aaa9ef76d1dbd87943aa387"
SRC_URI[openjdk.sha256sum] = "4911adb6d7877b014777b6db6d90f1d1626314bd0c6a2c9cf9911d1e11eb4b49"

# hotspot changeset taken from hotspot/tags
SRC_URI[hotspot.md5sum] = "5ffb731931226fbff870b80a377f6258"
SRC_URI[hotspot.sha256sum] = "984918bcb571fecebd490160935bb282c60eb9e17b4fc8fc77733d8da164c33a"

###############################################################################
# PATCHES - split up to allow overriding them separately
OEPATCHES = "\
    file://build-hacks.patch \
    file://fix_hotspot_crosscompile.patch \
    file://icedtea-makefile-unzip.patch \
"

ICEDTEAPATCHES = "\
    file://icedtea-zero-hotspotfix.patch;apply=no \
    file://icedtea-jdk-nio-use-host-cc.patch;apply=no \
    file://icedtea-jdk-rmi-crosscompile.patch;apply=no \
    file://icedtea-crosscompile-fix.patch;apply=no \
    file://icedtea-xawt-crosscompile-fix.patch;apply=no \
    file://icedtea-jdk-unzip.patch;apply=no \
    file://icedtea-dtrace-std_h.patch;apply=no \
"

DISTRIBUTION_PATCHES = "\
    patches/icedtea-zero-hotspotfix.patch \
    patches/icedtea-jdk-nio-use-host-cc.patch \
    patches/icedtea-jdk-rmi-crosscompile.patch \
    patches/icedtea-crosscompile-fix.patch \
    patches/icedtea-xawt-crosscompile-fix.patch \
    patches/icedtea-jdk-unzip.patch \
    patches/icedtea-dtrace-std_h.patch \
"

export DISTRIBUTION_PATCHES
