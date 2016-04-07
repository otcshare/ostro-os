.. _booting-and-installation:

Booting and Installing an Ostro |trade| OS Image
#################################################

This technical note explains the basic procedures for taking an Ostro OS image that was downloaded
or built from source (using instructions in :ref:`Building Images`), and installing and
running that image one of the :ref:`platforms`.

Two images are of interest for this process (depending if you're using real hardware or a VM):

:file:`.dsk.xz`
    A compressed raw disk image in GPT format and contains at least one UEFI bootable partition
    and at least one ext4 partition (rootfs).  For details on disk layout
    see the associated :file:`.json` file in the same directory as the image file.

:file:`.vdi`
    A :file:`.dsk` image converted to VirtualBox\* format (with no other differences).


Ostro OS Images
===============

As explained in the :ref:`Building Images` tech note, there are several image configurations available
depending on your need.  For simplicity and the needs of this tech note, we'll use the reference image that includes
additional configuration changes that wouldn't typically be included in a production device image. This
reference image will auto-login as ``root`` at the console, something that normally would not be available
in a production device image but is quite useful during development.


Using bmaptool to Create Bootable Media
=======================================

Once you have the :file:`.dsk.xz` Ostro OS image you need to get it
onto your hardware platform, typically by using removable media such as a
USB thumb drive or SD card.

The recommended way to do this is with the :command:`bmaptool` command from `bmap-tools`_.
A copy of this utility is available in the :file:`deploy/tools` folder after a Yocto Project build
for your image is finished.

The ``bmaptool`` program automatically handles copying either compressed and uncompressed images to
your removable media.  It also also uses a generated ``image.bmap`` file containing a checksum for
itself and for all mapped data regions in the image file, making it possible to verify data integrity
of the downloaded image. Be sure to download this ``.bmap`` file along with the image for your device.


#. Connect your USB thumb drive or SD card to your Linux-based development system
   (minimum 4 GB card required, for some images 8 GB card might be required).
#. If you're not sure about your media device name, use the :command:`dmesg` command to view the system log
   and see which device the USB thumb drive or SD card was assigned (e.g. :file:`/dev/sdb`)::

      $ dmesg

   or you can use the :command:`lsblk` command to show the block-level devices; a USB drive usually
   shows up as ``/sdb`` or ``/sdc``
   (almost never as ``/sda``) and an SD card would usually show up as :file:`/dev/mmcblk0`.

   Note: You should specify the whole device you're writing to with
   :command:`bmaptool`:  (e.g., :file:`/dev/sdb` or
   :file:`/dev/mmcblk0`) and **not** just a partition on that device (e.g., :file:`/dev/sdb1` or
   :file:`/dev/mmcblk0p1`) on that device.

#. The :command:`bmaptool` command will overwrite all content on the device so be careful specifying
   the correct media device. The ``bmaptool`` opens the removable media exclusively and helps prevent
   writing on an unintended device. After verifying your removable media device name, you'll need
   to ``umount`` the device before writing to it.

   In the example below, :file:`/dev/sdb` is the
   destination USB device on our development machine::

      $ sudo umount /dev/sdb*
      $ sudo -E bmaptool copy <ostro-os-image> /dev/sdb

.. note::
    The :command:`bmaptool` is intelligent enough to recognize images in different
    formats, including compressed images (.gz, .bz2, .xz) as well as flashing
    directly from remote URL (for example, you could specify the image source file with an
    ``http://`` address instead of downloading it first; ``bmaptool`` will automatically retrieve
    the .bmap file). The ``sudo -E`` option will propagate environment variables (such as http_proxy)
    that bmaptool might need to access the website.


Unplug the removable media from your development system and you're ready to plug
it into your target system.

.. _bmap-tools: http://git.infradead.org/users/dedekind/bmap-tools.git/blob/HEAD:/docs/README

Using dd to Create Bootable Media
=================================

While using ``bmaptool``  to create your bootable media is preferred because it's faster and
includes a checksum verification, you can also use the traditional :command:`dd` command instead :

#. Connect your USB thumb drive or SD card to your Linux-based development system
   (minimum 8 GB card required).
#. If you're not sure about your media device name, use the :command:`dmesg` command to view the system log
   and see which device the USB thumb drive or SD card was assigned (e.g. :file:`/dev/sdb`)::

      $ dmesg

   or you can use the :command:`lsblk` command to show the block-level devices; a USB drive usually
   shows up as ``/sdb`` or ``/sdc``
   (almost never as ``/sda``) and an SD card would usually show up as :file:`/dev/mmcblk0`.

   Note: You should specify the whole device you're writing to with
   :command:`dd`:  (e.g., :file:`/dev/sdb` or
   :file:`/dev/mmcblk0`) and **not** just a partition on that device (e.g., :file:`/dev/sdb1` or
   :file:`/dev/mmcblk0p1`) on that device.

#. The :command:`dd` command will overwrite all content on the device so be careful specifying
   the correct media device. In the example below, :file:`/dev/sdb` is the
   destination USB device on our development machine::

      $ sudo umount /dev/sdb*
      $ xzcat <ostro-os-image.dsk.xz> | sudo dd of=/dev/sdb bs=512k
      $ sync

Unplug the removable media from your development system and you're ready to plug
it into your target system.


MinnowBoard Turbot - a MinnowBoard MAX Compatible
=================================================

The `MinnowBoard Turbot`_ is a small form-factor board with an Intel |reg| Atom |trade| E3826 dual-core processor.
Once you have the Ostro OS image on a USB thumb drive (or SD card), you can use this to boot your MinnowBoard MAX compatible board as you would
most any Intel UEFI-based system.  The procedure will be similar for other boards so we’ll use this as an example.
See http://wiki.minnowboard.org for additional information about setting up the MinnowBoard hardware.

.. note::

    It's important to use a current version of firmware on your board, so we recommend checking this
    first and updating the firmware if needed using the instructions
    at http://wiki.minnowboard.org/MinnowBoard_MAX_HW_Setup.  Ostro OS releases are built and tested
    with 64-bit support, so you should make sure that the firmware is also setup for 64-bit support.

Here are the basic steps for booting the Ostro OS:

#. Connect an HDMI monitor, USB keyboard, and network cable. Alternatively you can connect the serial
   FTDI cable from the MinnowBoard to a USB port on your host computer and use a terminal emulator
   to communicate with the MinnowBoard.)
#. Plug in the USB thumb drive with your Ostro OS image to your MinnowBoard
#. Power the board on
#. Wait for the system to enter the EFI shell where you can set the system date and time with the :command:`date` and :command:`time`
   (Because the MinnowBoard MAX does not have a battery for the clock (RTC), the system date and time revert to the date and time
   when the firmware was created.)
#. Enter :command:`exit` to return to the boot option screen
#. Use the arrow keys to select Boot Manager, press return, then select EFI USB Device, and press return
#. The Ostro OS will begin booting and debug messages will appear on the terminal
#. A warning will appear indicating this is a development image and you will be automatically logged in as ``root`` (no password)

.. _MinnowBoard Turbot: http://wiki.minnowboard.org


Gigabyte
========

The `GigaByte GB-BXBT-3825 <http://iotsolutionsalliance.intel.com/solutions-directory/gb-bxbt-3825-iot-gateway-solution>`_
is a gateway solution powered by an Intel |reg| Atom |trade| E3825 dual-core processor
(64-bit images are supported). Booting is similar to booting a
MinnowBoard MAX from the USB thumbdrive described above.

Galileo Gen 2
=============

The `Intel Galileo Gen 2`_ is an Intel® Quark x1000 32-bit, single core, Intel Pentium |reg| Processor class
SOC-based board, pin-compatible with shields designed for the Arduino Uno R3.

Flashing an `Intel Galileo Gen 2`_ requires use of a microSD card (booting off USB is not supported).

Here are the basic steps for booting the Ostro OS:

#. Flash the microSD card with the Ostro OS image as described in the `Using dd to Create Bootable Media`_ section above
#. Insert the microSD card in the Galileo Gen 2 board
#. Connect the serial FTDI cable from the `Intel Galileo Gen 2`_ to a USB port on your host computer and use a terminal emulator (settings: 115200 8N1)
#. Power the board on (using a 5V, 3A power supply)
#. Press [Enter] to directly boot
#. The Ostro OS will begin booting and debug messages will appear on the terminal
#. A warning will appear indicating this is a development image and you will be automatically logged in as ``root`` (no password)

.. _Intel Galileo Gen 2: http://www.intel.com/content/www/us/en/embedded/products/galileo/galileo-overview.html

Intel Edison
============

Flashing an Intel Edison requires use of a breakout board and two micro-USB cables:

#. Install the ``dfu-util`` package. (You may also need the ``xfstk`` utility from http://xfstk.sourceforge.net
   for recovery cases.)
#. Plug in a micro-USB cable to the J3 connector on the board (corner next to the FTDI chip).
#. Flip the DIP switch towards jumper J16.
#. Download the ``ostro-image-swupd-reference`` image from the Ostro OS download folder for
   Edison (on https://download.ostroproject.org/releases/ostro-os/milestone/).
#. Extract the image from the archive using the command::

   $ tar xf ostro-image-*-edison-*.toflash.tar.bz2

#. Change directory to the toFlash folder.
#. Run the command::

   $ sudo ./flashall.sh

   `NOTE:` If the script is unable to find the image, use the ``-i <imagename>`` option to the flashall script.
#. Plug in the second micro-USB cable to the J16 connector as instructed by the running flashall script.
#. Wait for all the images to flash. You will see the progress on the flasher.
#. Once flashing is done, the image will automatically boot up and auto-login as ``root``, no password is required.

BeagleBone Black
================

BeagleBone Black is booted from a microSD card with MBR (Master Boot Record) and not GPT (GUID Partition Table) partitions.
Most freshly unpackaged microSD cards come with MBR partitions, but previously used ones might not.  (We have
instructions below to properly initialize the microSD card.)

You'll probably need an adapter to use the microSD card on your host computer. If you use a microSD-to-SD adapter,
it will likely show up as ``/dev/mmcblk0`` when plugged into your host computer.  If you use a USB adapter, it
will show up as ``/dev/sdb`` or ``/dev/sdc``.  (On some computers with a built-in SD-card slot, the card may also
show up as ``/dev/sdX`` rather than ``/dev/mmcblkX``.)


You can verify the device name assigned by using ``dmesg`` or the
``lsblk`` command to look for the device name for the microSD card (check for a device with the size you're expecting).

In our setup steps below, we're using an 8GB microSD card in an SD adapter that's showing up as ``/dev/mmcblk0``
(numbers and device name maybe different for your device and system).

.. comment:   steps derived from http://www.armhf.com/boards/beaglebone-black/bbb-sd-install/
.. _BeagleBone build 405 images: https://download.ostroproject.org/builds/ostro-os/2016-03-11_05-44-23-build-405/images/beaglebone/
.. _Ostro Project download server: http://download.ostroproject.org

1. We'll start by gathering files we'll put on the microSD card.  Aim your browser to the
   `Ostro Project download server`_ (if you're not doing your own build).
   The ``releases`` folder contains milestone builds of the Ostro OS, while the
   ``builds`` folder has non-milestone builds.  For this example, we're using the `BeagleBone build 405 images`_ folder.

   Download these four files to your host computer::

      MLO
      ostro-image-swupd-reference-beaglebone-*.rootfs.tar.bz2
      u-boot.img
      zImage-am335x-boneblack.dtb

   In our example below, we're using the development (``-dev``) image. the process for creating a bootable SD card is the same
   for all the image variants. (Image variants are explained in :ref:`Building Images`.)

.. _creating partitions:

2. Now we're ready to prepare the microSD card.  Make sure the microSD card isn't already mounted
   and verify it is using MBR partitions. (Remember, your
   device name maybe different than what we're using in our examples.) Run ::

   $ sudo umount /dev/mmcblk0*
   $ sudo fdisk /dev/mmcblk0

   If you get an error saying "unable to open /dev/mmcblk0" then you should
   verify the device name assigned as described above.
   If you get an error that GPT partitions are used, see the
   section below on `Converting from GPT to MBR Partitions`_ and then return to retry this step.

   If all is well, you'll see the fdisk prompt::

      Command (m for help):

#. We want to create two partitions on the SD card: a small primary bootable active partition,
   and a second primary linux root filesystem partition for the remaining space on the device.  The
   following ``fdisk`` commands will clean out all the existing partition information and set up two partitions:

   a. Initialize the partition table by typing **o**.
   b. Create the boot partition by typing **n** for "new", then **p** for "primary", and **1** to specify the first partition.
      Press enter to accept the default first sector and specify 4095 for the last sector.
   c. Set the partition type to FAT16 by typing **t** for "type" and **e** for "W95 FAT16 (LBA)".
   d. Set the partition active (bootable) by typing **a** then **1** (for partition 1).
   e. Next, create the root filesystem by typing **n** for "new", then **p** for "primary",
      and **2** for the second partition. Accept the default values for the first and last sectors by pressing enter twice.
   f. Type **p** to "print" the partition table. It should look about like this::

        ...
        Device          Boot    Start      End   Blocks     Id  System
        /dev/mmcblk0p1    *      2048     4095     1024      e  W95 FAT16 (LBA)
        /dev/mmcblk0p2           4096 15523839   775872     83  Linux

   g. Finally, write these changes to the microSD card by typing **w** to "write" the partition table and exit.

#. At this point your microSD card is partitioned correctly but the partitions need to be formatted with
   partition 1 as FAT16 and partition 2 as ext4 (the normal linux journaled filesystem)::

     $ sudo mkfs.vfat -F 16 /dev/mmcblk0p1
     $ sudo mkfs.ext4  /dev/mmcblk0p2

   This last ``mkfs``  command may take a few minutes to complete, depending on the size of your SD card.
   You may optionally disable periodic filesystem checks on this partition with the command::

     $ sudo tune2fs -c0 -i0 /dev/mmcblk0p2

#. Now we can install the ``MLO`` and ``u-boot.img`` (downloaded from `Ostro Project download server`_)
   to the first partition of our microSD card.   ::

     $ mkdir boot
     $ sudo mount /dev/mmcblk0p1 boot
     $ sudo cp MLO u-boot.img boot/
     $ sudo umount boot/

#. And we can install the Ostro OS root filesystem to the second partition on our microSD card.
   This step requires tar version 1.27 or later:  the xattrs flags are needed to preserve the Smack labels and IMA xattrs. ::

     $ mkdir rootfs
     $ sudo mount /dev/mmcblk0p2 rootfs
     $ sudo tar xvjf ostro-image-swupd-reference-beaglebone*.rootfs.tar.bz2 --wildcards --xattrs --xattrs-include=*  -C rootfs

#.  Before unmounting the device, we also need to add the device tree blob file (``zImage-am335x-boneblack.dtb``)
    that you downloaded (or from your own build).
    Note that this step renames the file (without the ``zImage-`` prefix) to match what's expected by the kernel ::

     $ sudo cp zImage-am335x-boneblack.dtb rootfs/boot/am335x-boneblack.dtb
     $ sudo umount rootfs

#. Remove the SD card from your host computer, remove the microSD card from its adapter,
   insert the microSD card into the BeagleBone Black (slot is on the bottom of the board) and power up the device.

Note:  The normal boot sequence is to use the on-board flash first (eMMC), then the microSD card,
then the USB port, and finally the serial port. You may need to use the **S2** alternate boot button,
by holding it down at power up, to change the boot order to use the microSD card first instead of eMMC first.

Once booted from the microSD card, you can prevent boot from eMMC by using (on the BeagleBone Black) ::

   $ dd if=/dev/zero of=/dev/mmcblk1 bs=4M count=1


Converting from GPT to MBR Partitions
-------------------------------------

On a linux system run the ``gdisk`` utility *(Note: your microSD card device name may be different than in this example)* ::

   $ sudo umount /dev/mmcblk0*
   $ sudo gdisk /dev/mmcblk0

   Command (? for help): x       # enter expert mode

   Expert command (? for help): z
   About to wipe out GPT on /dev/mmcblk0.  Proceed? (Y/N): y
   GPT data structure destroyed! You may now partition the disk using fdisk or
   other utilities.
   Blank out MBR? (Y/N): y

At this point we have a wiped microSD card ready for `creating partitions`_ as described above:
``fdisk`` will initialize the SD card with MBR partitions when it sees
the partition tables are wiped out.


Running Ostro OS in a VirtualBox\* VM
======================================

You can run an Ostro OS image within a VirtualBox virtual machine by using the pre-built ``.vdi`` file found
in the binary release directory (on https://download.ostroproject.org), or as the result of doing your
own build from source.  As with the other examples above, we recommend you start with the "dev" image.

#. If you have not already done so, download and install VirtualBox (version 5.0.2 or later)
   on your development system from https://www.virtualbox.org/wiki/Downloads. VirtualBox uses
   VDI as its native disk image format so you’ll be using that file instead of the .dsk file used
   with real hardware platforms.
#. Open the VirtualBox program and start by creating a new machine, give it a name
   (such as "Ostro OS build#"), select "Linux" for the VM type, and
   "Fedora (64-bit)" for the version.  Click next.
#. Use a minimum of 256MB RAM for the memory configuration. You can increase this if your application needs more. Click next.
#. Select "Use an existing virtual hard disk file", click on the folder icon and select the ``.vdi`` file you downloaded
   or created, and select "Create" to create the hard drive.
#. Click on the System options and remove all the boot order options other than the "Hard Disk", and check "Enable EFI (special OSes only)".
   While still on the system configuration, click on the "Acceleration" tab and verify that
   "Enable VT-x/AMX-V" (HW virtualization support) is checked. Click OK.
#. Finally, click on the "Start" arrow button and your new virtual machine will start
   booting the Ostro OS reference image and auto-login as root, no password is required.

If booting fails with a kernel panic, verify you’re using VirtualBox version 5.0.2 or later.  You can shut the machine down
by either using the :command:`shutdown now` within the running Ostro OS image, or by using the VirtualBox menu
Machine/ACPI-shutdown.


