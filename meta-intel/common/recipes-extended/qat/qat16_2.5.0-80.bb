include qat16.inc

SRC_URI += "https://01.org/sites/default/files/page/qatmux.l.${PV}.tgz;name=qat \
            file://qat16_2.5.0-80-qat-add-install-target-to-makefiles.patch \
            "

SRC_URI[qat.md5sum] = "e3c2ceeec7ed8b36d75682742caff81e"
SRC_URI[qat.sha256sum] = "e9e47cd9cbd98c2ceac5cc31570e443680649be682068126df6d749120a3697d"

do_install_append() {
        install -m 0755 ${SAMPLE_CODE_DIR}/performance/compression/calgary32 ${D}${base_libdir}/firmware
}
