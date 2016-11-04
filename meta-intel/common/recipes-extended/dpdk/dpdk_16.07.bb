include dpdk.inc

SRC_URI += "\
            file://dpdk-16.04-add-config-variable-to-enable-disable-dpdk_qat.patch \
            file://dpdk-16.04-dpdk-enable-ip_fragmentation-in-common_base-config.patch \
            "

SRC_URI[dpdk.md5sum] = "4afdc7951e21ff878a85ecade7f6f488"
SRC_URI[dpdk.sha256sum] = "cc982455a74357e465112bede5c29451b6eeb35f8c1c0dcea280dd3e7829f0e9"

export EXAMPLES_BUILD_DIR = "${RTE_TARGET}"
export ARCHDIR = "generic"

do_configure_prepend () {
	sed -e "s#CONFIG_RTE_LIBRTE_POWER=y#CONFIG_RTE_LIBRTE_POWER=${CONFIG_EXAMPLE_VM_POWER_MANAGER}#" -i ${S}/config/common_linuxapp
}
