SUMMARY = "Update Intel CPU microcode"

DESCRIPTION = "iucode_tool is a program to manipulate Intel i686 and X86-64\
 processor microcode update collections, and to use the kernel facilities to\
 update the microcode on Intel system processors.  It can load microcode data\
 files in text and binary format, sort, list and filter the microcode updates\
 contained in these files, write selected microcode updates to a new file in\
 binary format, or upload them to the kernel. \
 It operates on microcode data downloaded directly from Intel:\
 http://feeds.downloadcenter.intel.com/rss/?p=2371\
"
HOMEPAGE = "https://gitlab.com/iucode-tool/"
BUGTRACKER = "https://bugs.debian.org/cgi-bin/pkgreport.cgi?ordering=normal;archive=0;src=iucode-tool;repeatmerged=0"

LICENSE = "GPLv2+"
LIC_FILES_CHKSUM = "file://COPYING;md5=751419260aa954499f7abaabaa882bbe \
                    file://iucode_tool.c;beginline=1;endline=15;md5=5d8e3639c3b6a80e7d5e0e073933da16"

DEPENDS_append_libc-musl = " argp-standalone"

SRC_URI = "https://gitlab.com/iucode-tool/releases/raw/master/iucode-tool_${PV}.tar.xz"
SRC_URI_append_libc-musl = " file://0001-Makefile.am-Add-arg-parse-library-for-MUSL-support.patch"

SRC_URI[md5sum] = "306d20b43da847812af4bf973f46045d"
SRC_URI[sha256sum] = "8f94ec73f5d4d1a6801aaa894fa1c6544d9b27aec16e1a00e18e8241c7e0f6ba"

inherit autotools

BBCLASSEXTEND = "native"

COMPATIBLE_HOST = "(i.86|x86_64).*-linux"
