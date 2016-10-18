include qat16.inc

SRC_URI += "https://01.org/sites/default/files/page/qatmux.l.2.6.0-60.tgz;name=qat \
            file://qat16_2.6.0-65-qat-add-install-target-to-makefiles.patch \
            file://qat16_2.6.0-65-qat-override-CC-LD-AR-only-when-it-is-not-define.patch \
           "

SRC_URI[qat.md5sum] = "c54e877fb9fbb4690a9bd50793268bcf"
SRC_URI[qat.sha256sum] = "872046ffdf02f664d12a56cdb880403d65b914b303b75875707a9eebd9c841f5"

do_install_append() {
        install -m 0755 ${SAMPLE_CODE_DIR}/performance/compression/calgary32 ${D}${base_libdir}/firmware
}
