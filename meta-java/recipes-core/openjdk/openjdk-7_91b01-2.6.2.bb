require openjdk-7-common.inc

LIC_FILES_CHKSUM = "file://COPYING;md5=59530bdf33659b29e73d4adb9f9f6552"

FILESPATH =. "${FILE_DIRNAME}/patches-openjdk-7:"

inherit distro_features_check

REQUIRED_DISTRO_FEATURES = "x11"

PR = "${INC_PR}.1"

SRC_URI[iced.md5sum] = "a16b3e800030db9d9b35f80dfd11883a"
SRC_URI[iced.sha256sum] = "c19eafacd23c81179934acab123511c424cd07c094739fa33778bf7cc80e14d0"

CORBA_CHANGESET = "a4d55c5cec23"
SRC_URI[corba.md5sum] = "e673f3df063c54d0dda32963e4980605"
SRC_URI[corba.sha256sum] = "0b3bfa11c912c44b83248f5bb9c630c292409c6137951cd249f8f24c344ec4ad"

JAXP_CHANGESET = "f1202fb27695"
SRC_URI[jaxp.md5sum] = "2088e60c6893b1ecf127be3c2bcd4dd8"
SRC_URI[jaxp.sha256sum] = "53de0b094e2bcc173153f5d2fcd3886e8bd9feedec6510474e27ab38472088fc"

JAXWS_CHANGESET = "14c411b1183c"
SRC_URI[jaxws.md5sum] = "d2474c78e7e300b1b8ebb767209df587"
SRC_URI[jaxws.sha256sum] = "2c176962cab52263d3b819a303fa0ac29216a3edcddf75b39595e073da13580f"

JDK_CHANGESET = "db69ae53157a"
SRC_URI[jdk.md5sum] = "5de142350438baf9e4afee021966681a"
SRC_URI[jdk.sha256sum] = "782c8636475eef9f130718006c20be55974055a8505e241768816f6afd431666"

LANGTOOLS_CHANGESET = "73356b81c5c7"
SRC_URI[langtools.md5sum] = "f607b5d230c96afb33da25d9f9968b30"
SRC_URI[langtools.sha256sum] = "eac950fb11b55ecae9a3fec6127cfe48595d02c10a8cad0525b64160463eedf2"

OPENJDK_CHANGESET = "601ca7147b8c"
SRC_URI[openjdk.md5sum] = "d5c5a54d79e0cf9456c370e578aadbd1"
SRC_URI[openjdk.sha256sum] = "c1e6924bddff0ddec318364c60f4e0843c1186a0aa9911ce6cf2fd81164cd6a7"

# hotspot changeset taken from hotspot/tags
HOTSPOT_CHANGESET = "3f1b4a1fe4a2"
SRC_URI[hotspot.md5sum] = "106b2ec0a8798fbe07f3d838568bd0d8"
SRC_URI[hotspot.sha256sum] = "39bc54bf343e1dce404b8c95285c0457a8d0a7c7aedfb55055aff9795dd36a85"

###############################################################################
# PATCHES - split up to allow overriding them separately
OEPATCHES = "\
	file://build-hacks.patch \
	file://fix_hotspot_crosscompile.patch \
	"

ICEDTEAPATCHES = "\
	file://icedtea-zero-hotspotfix.patch;apply=no \
	file://icedtea-jdk-nio-use-host-cc.patch;apply=no \
	file://icedtea-jdk-build-nio-gensor-genuc-gensc-static.patch;apply=no \
	file://icedtea-jdk-rmi-crosscompile.patch;apply=no \
	file://icedtea-crosscompile-fix.patch;apply=no \
	file://icedtea-xawt-crosscompile-fix.patch;apply=no \
	"

DISTRIBUTION_PATCHES = "\
	patches/icedtea-zero-hotspotfix.patch \
	patches/icedtea-jdk-nio-use-host-cc.patch \
	patches/icedtea-jdk-build-nio-gensor-genuc-gensc-static.patch \
	patches/icedtea-jdk-rmi-crosscompile.patch \
	patches/icedtea-crosscompile-fix.patch \
	patches/icedtea-xawt-crosscompile-fix.patch \
	"

export DISTRIBUTION_PATCHES
