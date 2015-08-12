require openjdk-7-release-85b01.inc

PR = "${INC_PR}.1"

SRC_URI[iced.md5sum] = "efac44117a94b9d3278988959e336e05"
SRC_URI[iced.sha256sum] = "491866e57199b0bc99d716be3eabaab97d9f6a698d1a652d748baeddeedfe963"

CORBA_CHANGESET = "2545636482d6"
SRC_URI[corba.md5sum] = "7e821a5fb388d7ba0e29bcadbafea7ac"
SRC_URI[corba.sha256sum] = "e91886a9e5e1bf5a481bf1bdc9f51a73cfadfc785e06a9d0af754c18b4c7d07a"

JAXP_CHANGESET = "ffbe529eeac7"
SRC_URI[jaxp.md5sum] = "d28f58c41fa71553cf110e0a2d1fdf05"
SRC_URI[jaxp.sha256sum] = "2bd11bbd6a9ca5374353db5fa6c45cba1645e628af3c03e614fee1a79baec271"

JAXWS_CHANGESET = "b9776fab65b8"
SRC_URI[jaxws.md5sum] = "87aaa809c958e45ab882001cdf03a7dd"
SRC_URI[jaxws.sha256sum] = "1892b1366b9ae90ceb41547067ca79c3e113ecc1eb8bcf447c81768d25b1a1a5"

JDK_CHANGESET = "61d3e001dee6"
SRC_URI[jdk.md5sum] = "01c56e39df95192cb2542f961b846e1c"
SRC_URI[jdk.sha256sum] = "4bf866f2da37b7391fa89d205eaa8ad21c56953a922d8969ccfbd77b982dfba9"

LANGTOOLS_CHANGESET = "9c6e1de67d7d"
SRC_URI[langtools.md5sum] = "b47e31b700ba156e86599eef5994550c"
SRC_URI[langtools.sha256sum] = "b5fbf91d0af014deb8a3ae3e8ee8d807f8c859351bc5bb767b3597cbe14b8acd"

OPENJDK_CHANGESET = "39b2c4354d0a"
SRC_URI[openjdk.md5sum] = "3732dfebef27c22ef39fd2280c8fd0ac"
SRC_URI[openjdk.sha256sum] = "05725e6d4abccf657ed56064d03a2f0ef38363e2ff96011921c948341bcaebe6"

# hotspot changeset taken from hotspot/tags
HOTSPOT_CHANGESET = "3f1b4a1fe4a2"
SRC_URI[hotspot.md5sum] = "106b2ec0a8798fbe07f3d838568bd0d8"
SRC_URI[hotspot.sha256sum] = "39bc54bf343e1dce404b8c95285c0457a8d0a7c7aedfb55055aff9795dd36a85"
