DEPENDS_append_intel-x86-common = " rmc"

FILESEXTRAPATHS_prepend := "${THISDIR}/systemd-boot:"

EXTRA_OEMAKE_append_intel-x86-common = ' EFI_LDFLAGS="-L${STAGING_DIR_HOST}/usr/lib" EFI_CFLAGS="-I${STAGING_INCDIR}/rmc -DRMC_EFI"'

# Pin systemd revision down for systemd-boot recipe.
# Patches could not be applied cleanly when systemd in OE is updated,
# though we don't expect a lot of changes could happen in bootloader.
# RMC is designed to support a large number of types of boards, so we
# should do explicit update with validation to prevent regression even
# resolving conflicts for a new tip could be done in a short time.

# Revision: systemd v232 in OE
SRCREV_intel-x86-common = "a1e2ef7ec912902d8142e7cb5830cbfb47dba86c"

SRC_URI_append_intel-x86-common = " \
            file://0001-sd-boot-Link-RMC-library-into-bootloader-and-stub.patch \
            file://0002-sd-boot-Load-board-specific-boot-entries-from-RMC-da.patch \
            file://0003-sd-boot-Support-global-kernel-command-line-fragment.patch \
            file://0004-sd-boot-Support-global-kernel-command-line-fragment-in-EFI-stub.patch \
            file://0001-efi-boot.c-workaround-for-Joule-BIOS-hang.patch \
            file://0001-sd-boot-stub-check-LoadOptions-contains-data.patch \
            "

PACKAGE_ARCH_intel-x86-common = "${INTEL_COMMON_PACKAGE_ARCH}"
