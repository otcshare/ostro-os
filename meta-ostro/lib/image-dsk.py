#~/usr/bin/python

import random
import string
import json
import os
import sys
from re import search, sub
from glob import glob
from uuid import uuid4
from subprocess import check_call

VARS = dict([x.split('=', 1) for x in sys.argv[1:]])

def lookup_var(varname, location=None):
    '''Look up a variable in the parameters or the environment.'''
    if varname in VARS:
        return VARS[varname]
    if varname in os.environ:
        return os.environ[varname]
    exit("image-dsk.py: variable %s%s not passed by image-dsk.bbclass, add it to the parameters." %
         (varname, ("used in " + location) if location else ""))

def symlink(src, dst):
    ''' Helper for symlink housekeeping. '''
    if os.path.exists(dst):
        os.remove(dst)
    os.symlink(src, dst)

# Uses a raw partition generated elsewhere.
def populate_rawcopy(src, dst):
    shutil.copyfile(src, dst)

# Creates and populates a FAT partition, out of a root directory.
def populate_vfat(src, dst):
    check_call(['mkdosfs', dst])
    check_call(['mcopy', '-i', dst, '-s'] + glob(src + '/*') + ['::/'])

# Creates and populates an ext4 partition out of a root directory.
def populate_ext4(src, dst):
    check_call(['mkfs.ext4', '-F', dst] + (['-d', src] if src else []))

def expand_vars(string, location=None):
    return sub(r'\$\{([^}]+)\}', lambda x: lookup_var(x.group(1), location), string)

# Entry point for generating the disk image.
def do_dsk_image():
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
            rootfs_key = key
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
                     expand_vars('${BPN}-${MACHINE}-disk-layout.json'))
    with open(disk_layout_file, 'w') as disk_layout:
        json.dump(obj=partition_table, fp=disk_layout,
                  indent=4, separators=(',', ': '))
    symlink(expand_vars('${IMAGE_NAME}-disk-layout.json'),
            disk_layout_file_link)

    # First step in creating the full disk image: loop file + GPT partition.
    full_image_name = \
        os.path.join(expand_vars("${DEPLOY_DIR_IMAGE}"),
                     expand_vars('${IMAGE_NAME}.dsk'))
    full_image_name_link = \
        os.path.join(expand_vars("${DEPLOY_DIR_IMAGE}"),
                     expand_vars('${BPN}-${MACHINE}.dsk'))
    check_call(['truncate',  '-s', str(full_image_size_mb) + 'M',
               full_image_name])
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
        full_partition_name_symlink = \
            os.path.join(expand_vars("${DEPLOY_DIR_IMAGE}"),
                         expand_vars('${BPN}-${MACHINE}.') + \
                         partition_table[key]["name"] + ".part")
        # Create the temporary loop file for hostong the partition.
        check_call(['truncate', '-s', str(partition_size_mb) + 'M',
                    full_partition_name])
        # Populate the partition accordingly to its parameters.
        eval('populate_' + str(partition_table[key]["filesystem"]) + \
             '("' + expand_vars(partition_table[key]["source"])+ '", "' + \
                    full_partition_name + '")')
        # Allocate space for the partition in the image loop file.
        check_call(['sgdisk', '-c=0:' + partition_logical_name,
                    '-n=0:' + str(partition_start_mb) + 'M:+' +
                              str(partition_size_mb) + 'M',
                    '-t=0:' + partition_type,
                    '-u=0:' + str(partition_table[key]["uuid"]),
                    full_image_name])
        check_call(['dd', 'if=' + full_partition_name,
                          'of=' + full_image_name,
                          'bs=1M',
                          'conv=notrunc',
                          'seek=' + str(partition_start_mb)])
        # Remove the partition, now that it exists in the disk image.
        if os.path.exists(full_partition_name):
            os.remove(full_partition_name)
        partition_start_mb += partition_table[key]["size_mb"]

if __name__ == "__main__":
    do_dsk_image()
