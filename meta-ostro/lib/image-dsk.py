#!/usr/bin/env python
#
# Image creation class for GPT multi-partioned disk images for EFI systems.
#
# Copyright (C) 2015-2016 Intel Corporation
# Licensed under the MIT license

import json
import os
import sys
import shutil
from re import sub
from glob import glob
from uuid import uuid4
from subprocess import check_call
from bmaptools import Filemap

VARS = dict([x.split('=', 1) for x in sys.argv[1:]])


def lookup_var(varname, location=None):
    """Look up a variable in the parameters or the environment."""
    if varname in VARS:
        return VARS[varname]
    if varname in os.environ:
        return os.environ[varname]
    exit("image-dsk.py: variable %s%s not passed by image-dsk.bbclass,"
         " add it to the parameters." %
         (varname, ("used in " + location) if location else ""))


def symlink(src, dst):
    """Helper for symlink housekeeping."""
    if os.path.exists(dst):
        os.remove(dst)
    os.symlink(src, dst)


def populate_rawcopy(src, dst):
    """Argument src is a raw partition generated elsewhere."""
    shutil.copyfile(src, dst)


def populate_vfat(src, dst):
    """Create and populate a FAT partition, out of a root directory <src>."""
    check_call(['mkdosfs', dst])
    check_call(['mcopy', '-i', dst, '-s'] + glob(src + '/*') + ['::/'])


def populate_ext4(src, dst):
    """Create and populate an ext4 partition out of a root directory <src>."""
    check_call(['mkfs.ext4', '-F', dst] + (['-d', src] if src else []))


def expand_vars(arg_string, location=None):
    """Expand variables in arg_string."""
    return sub(r'\$\{([^}]+)\}', lambda x: lookup_var(x.group(1), location),
               arg_string)


def truncate_mib(fname, fsize):
    """Create sparse file with requested size (in MiB)."""
    with open(fname, "a+b") as fobj:
        fobj.truncate(int(fsize) * 1024 * 1024)


def sparse_copy(src_fname, dst_fname, offset_mib=0):
    """Efficiently copy sparse file to or into another file."""
    filemap = Filemap.filemap(src_fname)
    try:
        dst_file = open(dst_fname, 'r+b')
    except IOError:
        dst_file = open(dst_fname, 'wb')

    for first, last in filemap.get_mapped_ranges(0, filemap.blocks_cnt):
        start = first * filemap.block_size
        end = (last + 1) * filemap.block_size

        filemap._f_image.seek(start, os.SEEK_SET)
        dst_file.seek((offset_mib * 1024 * 1024) + start, os.SEEK_SET)

        chunk_size = 1024 * 1024
        to_read = end - start
        read = 0

        while read < to_read:
            if read + chunk_size > to_read:
                chunk_size = to_read - read
            chunk = filemap._f_image.read(chunk_size)
            dst_file.write(chunk)
            read += chunk_size
    dst_file.close()


def do_dsk_image():
    """Entry point for generating the disk image."""
    # Load the descripton of the disk layout.
    partition_table = json.loads(expand_vars('${DSK_IMAGE_LAYOUT}'))

    # Before adding up the size of each partition, add the size of the GPT
    full_image_size_mb = partition_table["gpt_initial_offset_mb"] + \
        partition_table["gpt_tail_padding_mb"]

    # The rootfs is special, because its PARTUUID must be aligned with
    # the kernel command line, to allow pivot-rooting.
    for key in sorted(partition_table.iterkeys()):
        if not isinstance(partition_table[key], dict):
            continue
        # Calculate the total image size.
        full_image_size_mb += partition_table[key]["size_mb"]
        # Generate randomized uuids, if required (uuid == 0)
        # Otherwise leave whatever was set in the configuration file.
        if str(partition_table[key]['uuid']) == '0':
            partition_table[key]['uuid'] = str(uuid4()).lower()
        # Store these for the creation of the UEFI binary
        if partition_table[key]['name'] == 'rootfs':
            # The rootfs partuuid is not randomized, because it is required
            # by the command line embedded in the efi-combo-binary
            # and it might be even preferrable to fix it to specific values
            # for each product.
            # Default to lower case, to avoid issues from camelcase.
            partition_table[key]["uuid"] = \
                expand_vars("${ROOTFS_PARTUUID_VALUE}").lower()

    # Save to disk the layout with the PARTUUIDs used, to facilitate the
    # job of accessing programmatically individual partitions.
    disk_layout_file = \
        os.path.join(expand_vars("${DEPLOY_DIR_IMAGE}"),
                     expand_vars('${IMAGE_NAME}-disk-layout.json'))
    disk_layout_file_link = \
        os.path.join(expand_vars("${DEPLOY_DIR_IMAGE}"),
                     expand_vars('${IMAGE_LINK_NAME}-disk-layout.json'))
    with open(disk_layout_file, 'w') as disk_layout:
        json.dump(obj=partition_table, fp=disk_layout,
                  indent=4, separators=(',', ': '))
    symlink(expand_vars('${IMAGE_NAME}-disk-layout.json'),
            disk_layout_file_link)

    # First step in creating the full disk image: loop file + GPT partition.
    full_image_name = \
        os.path.join(expand_vars("${DEPLOY_DIR_IMAGE}"),
                     expand_vars('${IMAGE_NAME}.dsk'))
    truncate_mib(full_image_name, full_image_size_mb)
    check_call(['sgdisk', '-o', full_image_name])

    partition_start_mb = partition_table["gpt_initial_offset_mb"]
    for key in sorted(partition_table.iterkeys()):
        if not isinstance(partition_table[key], dict):
            continue
        # Generate even more auxiliary variable
        partition_logical_name = str(partition_table[key]["name"])
        partition_size_mb = partition_table[key]["size_mb"]
        partition_name = expand_vars("${IMAGE_NAME}") + '.' + \
            partition_table[key]["name"] + ".part"
        partition_type = expand_vars(partition_table[key]["type"])
        full_partition_name = \
            os.path.join(expand_vars("${DEPLOY_DIR_IMAGE}"), partition_name)
        # Create the temporary loop file for hostong the partition.
        truncate_mib(full_partition_name, partition_size_mb)
        # Populate the partition accordingly to its parameters.
        eval('populate_' + str(partition_table[key]["filesystem"]) +
             '("' + expand_vars(partition_table[key]["source"]) + '", "' +
             full_partition_name + '")')
        # Allocate space for the partition in the image loop file.
        check_call(['sgdisk', '-c=0:' + partition_logical_name,
                    '-n=0:' + str(partition_start_mb) + 'M:+' +
                              str(partition_size_mb) + 'M',
                    '-t=0:' + partition_type,
                    '-u=0:' + str(partition_table[key]["uuid"]),
                    full_image_name])
        sparse_copy(full_partition_name, full_image_name, partition_start_mb)
        # Remove the partition, now that it exists in the disk image.
        if os.path.exists(full_partition_name):
            os.remove(full_partition_name)
        partition_start_mb += partition_table[key]["size_mb"]

if __name__ == "__main__":
    do_dsk_image()
