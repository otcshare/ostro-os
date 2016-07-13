#!/bin/sh

EFI_TYPE="EF00"
EFI_BACKUP_TYPE="2700"

ROOT_PARTUUID=`cat /proc/mounts | grep " / " | sed 's/\/dev\/disk\/by\-partuuid\/\([^ ]*\).*/\1/'`
ROOT_PARTITION=`ls -la "/dev/disk/by-partuuid/${ROOT_PARTUUID}" | sed -e 's/\(.*..\/..\/\)//'`
read ROOT_DEVICE ROOT_PARTITION_NUMBER <<< `echo ${ROOT_PARTITION} | sed 's/\(sd[a-z]\|mmcblk[0-9]\)\([0-9]\)\|p\([0-9]\)/\1 \2 \3/'`
ROOT_PARTITION_FULL_PATH="/dev/${ROOT_PARTITION}"
ROOT_DEVICE_FULL_PATH="/dev/${ROOT_DEVICE}"

PARTITION_PREFIX=`echo ${ROOT_DEVICE} | sed -e '/mmcblk.*/s/mmcblk.*/p/' -e '/sd.*/s/sd.*//'`
EFI_PARTITION_NUMBER=`sgdisk -p ${ROOT_DEVICE_FULL_PATH} | grep ${EFI_TYPE} | sed 's/[ \t]*\([0-9]\).*/\1/'`
EFI_BACKUP_PARTITION_NUMBER=`sgdisk -p ${ROOT_DEVICE_FULL_PATH} | grep ${EFI_BACKUP_TYPE} | sed 's/[ \t]*\([0-9]\).*/\1/'`
EFI_PARTITION_FULL_PATH="${ROOT_DEVICE_FULL_PATH}${PARTITION_PREFIX}${EFI_PARTITION_NUMBER}"
EFI_BACKUP_PARTITION_FULL_PATH="${ROOT_DEVICE_FULL_PATH}${PARTITION_PREFIX}${EFI_BACKUP_PARTITION_NUMBER}"

TMP_PATH="/tmp/mnt/"
EFI_PATH="/EFI/BOOT/"
EFI_INTERNAL_PATH="/EFI_internal_storage/BOOT/"
TARGET_EFI_PATH=

umount ${TMP_PATH} &> /dev/null
rm -rf ${TMP_PATH} &> /dev/null
mkdir ${TMP_PATH} &> /dev/null
mount ${EFI_PARTITION_FULL_PATH} ${TMP_PATH} &> /dev/null

cd ${TMP_PATH}/${EFI_PATH}
EFI_APP_NAME=`ls boot*.efi |sed "s/\(boot.*.efi\)/\1/"`
EFI_APP_FULL_PATH="${TMP_PATH}/${EFI_PATH}/${EFI_APP_NAME}"
ROOT_PARTUUID=`cat ${EFI_APP_NAME} |grep PARTUUID |sed 's/.*PARTUUID=\([^ ]*\).*/\1/'`

cd /boot/${EFI_PATH}
EFI_APP_ROOT_PARTUUID=`cat ${EFI_APP_NAME} |grep PARTUUID |sed 's/.*PARTUUID=\([^ ]*\).*/\1/'`
if [ "${ROOT_PARTUUID}" != "${EFI_APP_ROOT_PARTUUID}" ]; then
  cd /boot/${EFI_INTERNAL_PATH}
  EFI_APP_ROOT_PARTUUID=`cat ${EFI_APP_NAME} |grep PARTUUID |sed 's/.*PARTUUID=\([^ ]*\).*/\1/'`
  if [ "${ROOT_PARTUUID}" != "${EFI_APP_ROOT_PARTUUID}" ]; then
    echo "Couldn't find an EFI application matching the expected root PARTUUID."
    exit 1
  fi
fi
REFERENCE_EFI_APP_FULL_PATH=`pwd`"/${EFI_APP_NAME}"

diff ${EFI_APP_FULL_PATH} ${REFERENCE_EFI_APP_FULL_PATH} &> /dev/null
if [ $? -eq 0 ]; then
	echo "No change to the EFI combo application."
	exit 0
fi
echo "Upgrading the EFI combo application."

umount ${TMP_PATH} &> /dev/null
mount ${EFI_BACKUP_PARTITION_FULL_PATH} ${TMP_PATH} &> /dev/null
rm -f ${EFI_APP_FULL_PATH}
sync
cp -a ${REFERENCE_EFI_APP_FULL_PATH} ${EFI_APP_FULL_PATH} &> /dev/null
sync
umount ${TMP_PATH} &> /dev/null
sync
sgdisk -t ${EFI_PARTITION_NUMBER}:${EFI_BACKUP_TYPE} \
       -t ${EFI_BACKUP_PARTITION_NUMBER}:${EFI_TYPE} \
       ${ROOT_DEVICE_FULL_PATH}
sync
