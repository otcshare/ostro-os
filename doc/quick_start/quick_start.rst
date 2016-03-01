.. _quick_start:


Ostro |trade| OS Quick Start Guide
##################################

This quick start guide explains how to install the Ostro OS development environment on your
development system and to install and run applications on :ref:`platforms`.

Refer to the Ostro OS Release Notes in the Image Release area for specific details about capabilities and status
of features for the current release. 

You'll find a summary of resources to find Ostro OS images, source code,
documentation, and support systems in :ref:`access-support`


This guide describes two ways to get started with your investigation and use of the Ostro OS: 

* Download one of the pre-built Ostro OS images, ready to run on a supported hardware platform, or 
  emulated using a Virtual Machine.

* Download the source code, examine and customize the OS and packages, and use the `Yocto Project`_ tools 
  to generate a new image that is tailored to your specific application needs.

.. _`Yocto Project`: http://yoctoproject.org



Prerequisites
=============

You can do Ostro OS development using a reasonable current Linux-based host
system capable of running Yocto Project tools used to configure and build 
Ostro OS images. You should be familiar
with the Yocto Project terminology and processes and how to use these tools as
documented at the `Yocto Project`_ web site.  A good place to start is with 
the `Yocto Project Quick Start Guide`_.

.. _`Yocto Project Quick Start Guide`: http://www.yoctoproject.org/docs/current/yocto-project-qs/yocto-project-qs.html

Downloading a Pre-Built Ostro OS Image
=======================================

A fast way to investigate the Ostro OS is to download one of the pre-built
Ostro OS images, ready to run on :ref:`platforms` (or emulated using a Virtual
Machine). Ostro OS images are available from  https://download.ostroproject.org

Within each of the hardware-specific release folders you’ll find an :file:`images` folder,
and in that folder, you'll find a :file:`.dsk` file that can be directly written to a hard disk 
or booted on a USB thumb drive (written there with :command:`dd`). This
:file:`.dsk` file contains a raw full-disk image with boot partition and rootfs
with sizes fixed at compile time.  For a faster download, you'll also find compressed versions of 
the ``.dsk`` file (with a ``.dsk.xz`` extension).

Note that the bit-support of the UEFI firmware on your hardware platform (such as a MinnowBoard
MAX) and for the Ostro OS distro must match; i.e., you need a 64-bit Ostro OS
image for a board with 64-bit firmware. Check the firmware version on your
board to verify which bit-support is configured.

Once you’ve downloaded the image for your supported hardware, you're ready to load
and run that image on your :ref:`platforms` or emulation environment.


Setting up and Building an Ostro OS Image
=========================================

If you don’t want to use one of the pre-built images, you can get the Ostro OS sources and make your 
own image. We've written a :ref:`Building Images` tech note that explains this procedure. 

You should be familiar with the `Yocto Project`_ build tools as 
explained in the `Yocto Project Quick Start Guide`_.  This guide has step-by-step instructions 
and system requirements for setting up your host computer’s development environment and 
tools needed to build an Ostro OS image.

Briefly (and as fully explained in the `Yocto Project Quick Start Guide`_), you’ll need:

*  A host system with a minimum of 50 Gbytes of free disk space that is running a supported 
   Linux distribution (i.e. recent releases of Fedora, openSUSE, CentOS, Debian, or Ubuntu). 
   If your host system supports multiple cores and threads, you can configure the Yocto Project
   build system to take advantage of this and significantly decrease the time needed to build images.

*  Appropriate developer packages (gawk, make, python, perl, patch, and others) 
   installed on the system you are using for builds

*  A release of the Yocto Project (included when you clone the ostroproject repo from GitHub).

Once you’ve followed the Yocto Project instructions to get your computer ready to host a project, 
you may also need to set up proxy information if your sitting behind a firewall.

You’ll also need to create an SSH public key (if you don’t already have one) and add that key to your GitHub 
profile as explained in these GitHub `Generating SSH Keys`_ instructions. (These instructions also show 
how to confirm that your proxy and SSH key are set correctly.)

.. _`Generating SSH Keys`: https://help.github.com/articles/generating-ssh-keys/

The `Yocto Project Quick Start Guide`_ offers detailed instructions and explanations about the build 
environment and processes. 

Briefly, you start by setting up the environment for building the Ostro OS by cloning the 
``ostroproject/ostro-os`` GitHub repo, editing configuration files, and then starting the build.  Refer to 
the :ref:`Building Images` tech note for more information.  

If you made no changes, you should end up with a binary :file:`.dsk` file 
that is functionally equivalent to an image in the Ostro Project binary release folder.

Running an Ostro OS image
==========================

Once you have an Ostro OS image (by downloading a pre-built image or by building your own), 
you’ll want to install and run it on your target hardware or VM environment.  We've written
a :ref:`booting-and-installation` tech note that explains this procedure.
