OSIP_STARTING_LBA = "2048"
OSIP_DESTINATION_POINTER = "17825792"
OSIP_HANDOFF_POINTER = "17829888"

# env is U-Boot primary environment where internal U-Boot variables are stored
# this default generated binary environment, is embedded in a raw OSIP image
# use by XFSTK tools to do the initial boot
ENV_IMAGE = "${S}/env.bin"
BASE_IMAGE = "${S}/u-boot.bin"
UBOOT_OSIP_SUFFIX = "img"
UBOOT_TMP_IMG = "${S}/u-boot.${UBOOT_OSIP_SUFFIX}.no-osip"
UBOOT_IMG = "${S}/u-boot.${UBOOT_OSIP_SUFFIX}"
UBOOT_OSIP_IMAGE = "u-boot-${MACHINE}-${PV}-${PR}.${UBOOT_OSIP_SUFFIX}"
UBOOT_OSIP_BINARY = "u-boot.${UBOOT_OSIP_SUFFIX}"
UBOOT_OSIP_SYMLINK = "u-boot-${MACHINE}.${UBOOT_OSIP_SUFFIX}"


do_uboot_padding() {
    # U-Boot.bin map
    # 0x000000 - 0x001000 | padding with 0
    # 0x001000 - 0x200000 | u-boot0
    dd if=/dev/zero of=u-boot.padding bs=4096 count=1
    cat u-boot.padding ${BASE_IMAGE} | dd of=u-boot.bin.padded

    # Align u-boot.bin to 4K for dfu
    filesize=$(stat -c %s u-boot.bin.padded)
    alignment=$(echo "4096 - (${filesize} % 4096)" | bc)
    if [ ${alignment} -ne 0 ];
    then
      dd if=/dev/zero of=u-boot.bin.padded bs=1 count=${alignment} conv=notrunc seek=${filesize}
   fi

    cp u-boot.bin.padded ${BASE_IMAGE}
}

do_uboot_uboot_env_mkimage() {

    # U-Boot.img map
    # 0x000000 - 0x001000 | padding with 0
    # 0x001000 - 0x200000 | u-boot0
    # 0x200000 - 0x300000 | primary environment
    # 0x300000 - 0x500000 | reserved
    # 0x500000 - 0x600000 | secondary environment

    # U-Boot.img on eMMC in LBA (LBA size: 512 bytes)
    #                     | description                | OSII | GPT label
    # 0x000000 - 0x000001 | MBR + OSIP                 | -    | -
    # 0x000001 - 0x000022 | GPT                        | -    | -
    # 0x000022 - 0x000800 | padding with 0 (alignment) | -    | -
    # 0x000800 - 0x001800 | u-boot0                    | 1    | u-boot0
    # 0x001800 - 0x002600 | primary environment        | -    | u-boot-env0
    # 0x002600 - 0x003600 | u-boot1                    | 2    | u-boot1
    # 0x003600 - 0x004400 | secondary environment      | -    | u-boot-env1


    # Fill U-Boot.img with 0
    dd if=/dev/zero of=${UBOOT_TMP_IMG} bs=6M count=1
    # copy u-boot.bin in u-boot.img (u-boot0)
    dd if=${BASE_IMAGE} of=${UBOOT_TMP_IMG} bs=1M conv=notrunc
    # copy (offset 2M) u-boot_env0.bin in u-boot.img (u-boot0)
    dd if=${ENV_IMAGE} of=${UBOOT_TMP_IMG} bs=1M conv=notrunc seek=2
    # copy (offset 5M) u-boot_env1.bin in u-boot.img (u-boot0)
    dd if=${ENV_IMAGE} of=${UBOOT_TMP_IMG} bs=1M conv=notrunc seek=5
}

python do_osip_mkimage() {
    #
    # Stitch an image to create an OSIP image (OS Image Profile).
    # This script currently supports only one OSII (OS Image Identifier)
    # If more is necessary, it will need to be adjusted.
    #
    # This is the C struct for one OSII (size = 24 bytes)
    # struct OSII {                   //os image identifier
    #   uint16_t os_rev_minor;
    #   uint16_t os_rev_major;
    #   uint32_t logical_start_block; //units defined by get_block_size() if
    #                                 //reading/writing to/from nand, units of
    #                                 //512 bytes if cracking a stitched image
    #   uint32_t ddr_load_address;
    #   uint32_t entry_point;
    #   uint32_t size_of_os_image;    //units defined by get_page_size() if
    #                                 //reading/writing to/from nand, units of
    #                                 //512 bytes if cracking a stitched image
    #   uint8_t attribute;
    #   uint8_t reserved[3];
    # };

    # This is what a full OSIP header contains
    # Its size is 512 bytes
    # Offset   Size (bytes) Description
    # 0x000       4         OSIP Signature "$OS$"
    # 0x004       1         Reserved
    # 0x005       1         Header minor revision
    # 0x006       1         Header major revision
    # 0x007       1         Header checksum
    # 0x008       1         Number of pointers
    # 0x009       1         Number of images
    # 0x00a       2         Header size
    # 0x00c      20         Reserved
    # 0x020      24         1st bootable image descriptor (OSII)
    # 0x038      24         2nd bootable image descriptor (OSII)
    # ...       ...         ...
    # 0x170      24         15th bootable image descriptor (OSII)
    # 0x188      48         Not used
    # 0x1B8       4         Disk signature
    # 0x1BC       2         Null (0x0000)
    # 0x1BE      16         1st primary partition descriptor
    # 0x1CE      16         2nd primary partition descriptor
    # 0x1DE      16         3rd primary partition descriptor
    # 0x1EE      16         4th primary partition descriptor
    # 0x1FE       1         0x55
    # 0x1FF       1         0xaa

    import os
    import sys
    import argparse
    import struct
    import binascii

    # As only a small portion of the OSIP header needs to be changed
    # we simply store a full binary copy and we'll change just the
    # necessary values in it
    OSIP_HEADER_HEX_DATA = \
    '244f532400000121010138000000000000000000000000000000000000' \
    '00000000000000220000000000100100101001380100000f000000ffff' \
    'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff' \
    'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff' \
    'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff' \
    'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff' \
    'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff' \
    'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff' \
    'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff' \
    'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff' \
    'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff' \
    'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff' \
    'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff' \
    'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff' \
    'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff' \
    'ffffffffff00000000000000000000ee0000000100000000e0a3030000' \
    '0000000000000000000000000000000000000000000000000000000000' \
    '000000000000000000000000000000000055aa'

    def main():
        input_file = d.getVar('UBOOT_TMP_IMG', True)
        output_file = d.getVar('UBOOT_IMG', True)
        handoff_pointer =  int(d.getVar('OSIP_HANDOFF_POINTER', True))
        destination_pointer = int(d.getVar('OSIP_DESTINATION_POINTER', True))
        starting_lba = int(d.getVar('OSIP_STARTING_LBA', True))

        in_file_data = open(input_file, 'rb').read()

        out_file = open(output_file, 'wb')

        # Write OSIP header data
        osip_header_data = bytearray(binascii.unhexlify(OSIP_HEADER_HEX_DATA))

        # Override some values

        # Overrides starting LBA of imge in eMMC
        starting_lba_packed = struct.pack("I", starting_lba)
        osip_header_data[0x24:0x27+1]=starting_lba_packed

        # Overrides destination pointer to image in DDR
        destination_pointer_packed = struct.pack("I", destination_pointer)
        osip_header_data[0x28:0x2B+1]=destination_pointer_packed

        # Overrides pointer to handoff entry point in image
        handoff_pointer_packed = struct.pack("I", handoff_pointer)
        osip_header_data[0x2C:0x2F+1]=handoff_pointer_packed

        # The file needs to be padded to be multiple of 512 bytes

        # Overrides passed image size (in unit of 512 bytes blocks)
        # (6*1024*1024) / 512) = 6*1024*2 used here to avoid
        # ambiguities around division: in Python2 it is the intended
        # integer division, in Python3 the result is a float.
        padding_len_packed_block = struct.pack("I", 6*1024*2)
        osip_header_data[0x30:0x33+1]=padding_len_packed_block

        # Compute XOR checksum
        osip_header_size = 1*0x18+0x20  # 24 bytes per OSII + 32 bytes header
        osip_header_data[0x07]=0
        crc = osip_header_data[0]
        for i in range(1, osip_header_size):
            crc ^= osip_header_data[i]
        osip_header_data[0x07]=crc

        out_file.write(osip_header_data)

        # Write image content
        out_file.write(in_file_data)

        out_file.close()

        return 0

    main()
}

do_deploy_append() {
    install -d ${DEPLOYDIR}
    install ${UBOOT_IMG} ${DEPLOYDIR}/${UBOOT_OSIP_IMAGE}

    cd ${DEPLOYDIR}
    rm -f ${UBOOT_IMG} ${UBOOT_OSIP_SYMLINK}
    ln -sf ${UBOOT_OSIP_IMAGE} ${UBOOT_OSIP_SYMLINK}
    ln -sf ${UBOOT_OSIP_IMAGE} ${UBOOT_OSIP_BINARY}
}

addtask uboot_padding before do_environment_mkimage before do_deploy after do_compile
addtask uboot_uboot_env_mkimage  before do_osip_mkimage after do_environment_mkimage
addtask osip_mkimage  before do_deploy after do_uboot_uboot_env_mkimage
