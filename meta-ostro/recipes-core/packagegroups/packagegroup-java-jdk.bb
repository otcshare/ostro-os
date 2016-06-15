SUMMARY = "Java JDK"
LICENSE = "MIT"

inherit packagegroup

# To avoid installing two different Java runtimes, we use the same one here
# that other packages already depend on via RDEPENDS, and in ostro.conf
# configure that to be what we want to have in Ostro OS.
RDEPENDS_${PN} = " \
    ${PREFERRED_RPROVIDER_java2-runtime} \
"
