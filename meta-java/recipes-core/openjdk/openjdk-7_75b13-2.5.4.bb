require openjdk-7-release-75b13.inc

PR = "${INC_PR}.1"

SRC_URI[iced.md5sum] = "646064d7a8d57c2cae0ef35a05de57c8"
SRC_URI[iced.sha256sum] = "5301b9a8592af2cf8e3e7a3650e5e1fe744c6d2de7f8ff78080b2eeae86a9800"

CORBA_CHANGESET = "3c9f523bf96e"
SRC_URI[corba.md5sum] = "fe08a1bdf6e5b9c6541f9ba5d12a8c7e"
SRC_URI[corba.sha256sum] = "da21a7e17c30f87f180a4e4712c32c382d9dc522c29736bb745cfc238bcea7a4"

JAXP_CHANGESET = "ca26767d3375"
SRC_URI[jaxp.md5sum] = "9479cc9bbe888cef835da2529fa6e07e"
SRC_URI[jaxp.sha256sum] = "d9e3c87357f0be354f7f76f820e97fb8fe918dd1bfeb223ff0958a662539f851"

JAXWS_CHANGESET = "9a6c90336922"
SRC_URI[jaxws.md5sum] = "a4cc532e6244637d2a185547075a057a"
SRC_URI[jaxws.sha256sum] = "b8154336679168deaa4fc076a1951f54073153d398ab840dfed3df456e4f4ae9"

JDK_CHANGESET = "1e6db4f8b0f3"
SRC_URI[jdk.md5sum] = "466b5bac22960beea959f79ef9029899"
SRC_URI[jdk.sha256sum] = "a5db2c28f23fee351aaa7fd783fbcd14a6f77c62d753fe6d52ab8b5b97a4720b"

LANGTOOLS_CHANGESET = "960cdffa8b3f"
SRC_URI[langtools.md5sum] = "a44baae860eafef49c6febb89c74acd8"
SRC_URI[langtools.sha256sum] = "daab93539d7c840865121f06dc7e0ec441656c2dc249ecee44aa2049643a4db3"

OPENJDK_CHANGESET = "6cf2880aab5e"
SRC_URI[openjdk.md5sum] = "b3c781de9e0632b61c6a61bc87d93631"
SRC_URI[openjdk.sha256sum] = "4387e53911667b6324421d9a1ea5c098fa5fb56a10f659124c1e10df3486e393"

# located in hotspot.map
# Replaced due to http://icedtea.classpath.org/bugzilla/show_bug.cgi?id=1851
HOTSPOT_CHANGESET = "67b77521a2fd"
SRC_URI[hotspot.md5sum] = "4bc7af1c7fd45c50ddfbb897730f0eb4"
SRC_URI[hotspot.sha256sum] = "050684e8c46b680728f477eba2546550d65ed3ded82329027f6163a3d8c5359a"
