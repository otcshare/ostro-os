include dpdk.inc

SRC_URI += "\
            file://dpdk-16.04-add-config-variable-to-enable-disable-dpdk_qat.patch \
            file://dpdk-16.04-dpdk-enable-ip_fragmentation-in-common_base-config.patch \
            "

SRC_URI[dpdk.md5sum] = "9ac25cffecbf550e145c45e53db03a3d"
SRC_URI[dpdk.sha256sum] = "b07b546e910095174bdb6152bb0d7ce057cc4b79aaa74771aeee4e8a7219fb38"

export EXAMPLES_BUILD_DIR = "${RTE_TARGET}"
export ARCHDIR = "generic"

do_configure_prepend () {
	sed -e "s#CONFIG_RTE_LIBRTE_POWER=y#CONFIG_RTE_LIBRTE_POWER=${CONFIG_EXAMPLE_VM_POWER_MANAGER}#" -i ${S}/config/common_linuxapp
}

COMPATIBLE_HOST_linux-gnux32 = "null"
COMPATIBLE_HOST_libc-musl_class-target = "null"
