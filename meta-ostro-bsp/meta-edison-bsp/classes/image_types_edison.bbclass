inherit image_types

IMAGE_DEPENDS_boot = "virtual/kernel:do_deploy dosfstools-native mtools-native"
IMAGE_TYPEDEP_boot = "ext4 tar"

IMAGE_TYPES += "boot update toflash"

# temporary assignment: only needed in combination with OE-core which doesn't
# have the variable yet.
IMGDEPLOYDIR ??= "${DEPLOY_DIR_IMAGE}"

IMAGE_CMD_boot () {

	BLOCKS=32768
	rm -f ${WORKDIR}/boot.img

	mkfs.vfat -n "boot" -S 512 -C ${WORKDIR}/boot.img $BLOCKS

	# Copy kernel
	mcopy -i ${WORKDIR}/boot.img -s ${DEPLOY_DIR_IMAGE}/bzImage-edison.bin ::/vmlinuz

	# Copy fota kernel (includes initramfs)
	if [ -e ${DEPLOY_DIR_IMAGE}/bzImage-initramfs-edison.bin ]; then
		mcopy -i ${WORKDIR}/boot.img -s ${DEPLOY_DIR_IMAGE}/bzImage-initramfs-edison.bin ::/vmlinuzi
	fi

	# Copy fota initramfs
	if [ -e ${DEPLOY_DIR_IMAGE}/core-image-initramfs-edison.cpio.gz ]; then
		mcopy -i ${WORKDIR}/boot.img -s ${DEPLOY_DIR_IMAGE}/core-image-initramfs-edison.cpio.gz ::/initramfs
	fi

	install ${WORKDIR}/boot.img ${IMGDEPLOYDIR}/${IMAGE_NAME}.hddimg
	ln -s -f ${IMAGE_NAME}.hddimg ${IMGDEPLOYDIR}/${IMAGE_BASENAME}-${MACHINE}.hddimg
}

IMAGE_DEPENDS_update = "dosfstools-native mtools-native"
IMAGE_TYPEDEP_update = "tar.bz2 boot"

IMAGE_CMD_update () {

	UPDATE_BLOCKS=786432
	FAT_BLOCKS=785408

	# clean up from previous builds
	rm -f ${WORKDIR}/update.img
	rm -f ${WORKDIR}/fat.img
	rm -f ${WORKDIR}/update.tar
	rm -f ${WORKDIR}/update.tar.gz


	# create disk image with fat32 primary partition on all available space
	dd if=/dev/zero of=${WORKDIR}/update.img bs=1024 count=$UPDATE_BLOCKS
	printf "n\np\n1\n\n\nt\nb\np\nw\n" | fdisk ${WORKDIR}/update.img

	# Create fat file system image
	mkfs.vfat -n "Edison" -S 512 -C ${WORKDIR}/fat.img $FAT_BLOCKS

	# Create recovery directory and populate it
	mmd -i ${WORKDIR}/fat.img ::/recovery
	echo ${IMAGE_NAME} > /tmp/image-name.txt
	mcopy -i ${WORKDIR}/fat.img -s /tmp/image-name.txt ::/recovery/image-name.txt	
	mcopy -i ${WORKDIR}/fat.img -s ${IMGDEPLOYDIR}/${IMAGE_BASENAME}-${MACHINE}.tar.bz2 ::/recovery/rootfs.tar.bz2
	mcopy -i ${WORKDIR}/fat.img -s ${IMGDEPLOYDIR}/${IMAGE_BASENAME}-${MACHINE}.hddimg ::/recovery/boot.hddimg
	mcopy -i ${WORKDIR}/fat.img -s ${DEPLOY_DIR_IMAGE}/u-boot-edison.bin ::/recovery/u-boot.bin
	mcopy -i ${WORKDIR}/fat.img -s ${DEPLOY_DIR_IMAGE}/u-boot-envs/edison-blankrndis.bin ::/recovery/u-boot.env

	# add fat image to disk image
	dd if=${WORKDIR}/fat.img of=${WORKDIR}/update.img bs=1024 seek=1024

	install ${WORKDIR}/update.img ${IMGDEPLOYDIR}/${IMAGE_NAME}.update.hddimg
	ln -s -f ${IMAGE_NAME}.update.hddimg ${IMGDEPLOYDIR}/${IMAGE_BASENAME}-${MACHINE}.update.hddimg

	# Create update archive
	tar -cf ${WORKDIR}/update.tar -C /tmp image-name.txt
	tar --transform='flags=r;s|${IMAGE_NAME}.rootfs.tar.bz2|rootfs.tar.bz2|' -rf ${WORKDIR}/update.tar -C ${IMGDEPLOYDIR} ${IMAGE_NAME}.rootfs.tar.bz2
	tar --transform='flags=r;s|${IMAGE_NAME}.hddimg|boot.hddimg|' -rf ${WORKDIR}/update.tar -C ${IMGDEPLOYDIR} ${IMAGE_NAME}.hddimg
	tar --transform='flags=r;s|u-boot-edison.bin|u-boot.bin|' -rhf ${WORKDIR}/update.tar -C ${DEPLOY_DIR_IMAGE} u-boot-edison.bin
	tar --transform='flags=r;s|edison-blankrndis.bin|u-boot.env|' -rf ${WORKDIR}/update.tar -C ${DEPLOY_DIR_IMAGE}/u-boot-envs edison-blankrndis.bin
	gzip ${WORKDIR}/update.tar

	install ${WORKDIR}/update.tar.gz ${IMGDEPLOYDIR}/${IMAGE_NAME}.update.tar.gz
	ln -s -f ${IMAGE_NAME}.update.tar.gz ${IMGDEPLOYDIR}/${IMAGE_BASENAME}-${MACHINE}.update.tar.gz
}

IMAGE_DEPENDS_toflash = "ifwi flashall u-boot-edison u-boot-mkimage-native"
IMAGE_TYPEDEP_toflash = "ext4 boot update"

IMAGE_CMD_toflash () {

	rm -rf 	${WORKDIR}/toFlash
	install -d ${WORKDIR}/toFlash/u-boot-envs/
	install -d ${WORKDIR}/toFlash/helper/images

	install ${IMGDEPLOYDIR}/${IMAGE_NAME}.rootfs.ext4	${WORKDIR}/toFlash/${IMAGE_BASENAME}-${MACHINE}.ext4
	install ${IMGDEPLOYDIR}/${IMAGE_NAME}.hddimg	${WORKDIR}/toFlash/${IMAGE_BASENAME}-${MACHINE}.hddimg
	install ${IMGDEPLOYDIR}/${IMAGE_NAME}.update.hddimg	${WORKDIR}/toFlash/${IMAGE_BASENAME}-${MACHINE}.update.hddimg

	install ${DEPLOY_DIR_IMAGE}/u-boot-edison.bin		${WORKDIR}/toFlash/
	install ${DEPLOY_DIR_IMAGE}/u-boot-edison.img		${WORKDIR}/toFlash/
	install ${DEPLOY_DIR_IMAGE}/u-boot-envs/*.bin		${WORKDIR}/toFlash/u-boot-envs/

	install ${DEPLOY_DIR_IMAGE}/ifwi/*.bin			${WORKDIR}/toFlash/

	install ${DEPLOY_DIR_IMAGE}/flashall/filter-dfu-out.js	${WORKDIR}/toFlash/
	install ${DEPLOY_DIR_IMAGE}/flashall/flashall.*		${WORKDIR}/toFlash/
	install ${DEPLOY_DIR_IMAGE}/flashall/pft-config-edison.xml ${WORKDIR}/toFlash/

	install ${DEPLOY_DIR_IMAGE}/flashall/FlashEdison.json	${WORKDIR}/toFlash/
	install ${DEPLOY_DIR_IMAGE}/flashall/helper/helper.html	${WORKDIR}/toFlash/helper/
	install ${DEPLOY_DIR_IMAGE}/flashall/helper/images/*.png ${WORKDIR}/toFlash/helper/images/

	# update image names inside flashing tools
	sed -e "s/^IMAGE_NAME=.\+$/IMAGE_NAME=\"${IMAGE_BASENAME}\"/" -i ${WORKDIR}/toFlash/flashall.sh
	sed -e "s/^set IMAGE_NAME=.\+$/set IMAGE_NAME=${IMAGE_BASENAME}/" -i ${WORKDIR}/toFlash/flashall.bat
	sed -e "s/\"edison-image-edison\./\"${IMAGE_BASENAME}-edison./" -i ${WORKDIR}/toFlash/FlashEdison.json

	# generate a formatted list of all packages included in the image
	awk '{print $1 " " $3}' ${IMGDEPLOYDIR}/${IMAGE_NAME}.rootfs.manifest > ${WORKDIR}/toFlash/package-list.txt

	tar cvjf ${IMGDEPLOYDIR}/${IMAGE_NAME}.toflash.tar.bz2 -C ${WORKDIR} toFlash/

	rm -f ${IMGDEPLOYDIR}/${IMAGE_BASENAME}-${MACHINE}.toflash.tar.bz2
	ln -s -f ${IMAGE_NAME}.toflash.tar.bz2 ${IMGDEPLOYDIR}/${IMAGE_BASENAME}-${MACHINE}.toflash.tar.bz2
}
