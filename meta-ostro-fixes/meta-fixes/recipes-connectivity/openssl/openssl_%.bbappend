# Upstream-Status: Submitted [https://bugzilla.yoctoproject.org/show_bug.cgi?id=9523]

do_install_ptest_append () {
    # openssl.inc links to /lib/libcrypto.a instead of the correct /usr/lib/libcrypto.a
    ln -sf ${libdir}/libcrypto.a ${D}${PTEST_PATH}
}
