.. _Building Images:

Building Ostro |trade| OS Images
################################

This technical note describes the basic instructions for building an Ostro |trade| OS image
from source using the Yocto Project tools.  You should already be familiar with these Yocto
Project tools, as explained in the `Yocto Project Quick Start Guide`_. 

.. _`Yocto Project Quick Start Guide`: http://www.yoctoproject.org/docs/current/yocto-project-qs/yocto-project-qs.html

Initial Steps
=============

#. If your development system is behind a firewall, verify that your proxy settings are configured 
   to allow access to    the internet for http, https, ftp, and git resources needed by 
   the Yocto Project build tools, as  explained in `Yocto Project Quick Start: Building Images`_ 
   and with more details in `Yocto Project: Working Behind a Network Proxy`_

#. Check out the ``ostro-os`` repository from the ``ostroproject`` GitHub area.  ::

   $ git clone https://github.com/ostroproject/ostro-os.git

   This clone command will retrieve the Ostro OS recipes
   and necessary Yocto Project tools and configuration files.  This ``ostro-os`` repository is a 
   combination of several different components gathered into a single repository. See the README 
   in the cloned copy you just made for up-to-date details on what’s included.)
#. In the repository folder you just cloned, setup the Yocto Project build environment. ::

   $ cd ostro-os
   $ source oe-init-build-env

   This will leave you in the ``ostro-os/build`` folder.

#. Edit the :file:`conf/local.conf` configuration text file and verify general configuration information is
   how you want it (more details about this in the sections below). In particular define which additional
   software that your want to have included and choose between building images in development or
   production configuration (build configurations without that choice will fail a sanity check and
   builds get aborted with an error message).

#. Be sure you're still in the ``ostro-os/build`` folder, and then generate an Ostro OS development 
   image using :command:`bitbake`. (additional build target options are explained
   in the sections below.) ::

   $ bitbake ostro-image-noswupd

   Depending on the number of processors and cores, the amount of RAM, the speed of the internet connection and
   other factors, the build process could take several hours the first time you run it. 
   It will download and compile all the source code needed to create the binary image, including the Linux kernel, 
   compiler tools, upstream components and Ostro OS-specific patches.  (If you haven't 
   done so yet, this might be a good time to read through 
   the `Yocto Project Quick Start Guide`_.) Subsequent builds
   run much faster since parts of the build are cached. 
          
   If errors occur during the build, refer to the `Yocto Project Errors and Warnings`_ documentation to help 
   resolve the issues, and repeat the ``bitbake ostro-image-noswupd`` command to continue.
   
   When the build process completes, the generated image will be in the folder 
   :file:`build/tmp-glibc/deploy/images/$(MACHINE)`

#. Copy this image to bootable media (such as a USB thumb drive or microSD card), and 
   boot the image you just generated on your target hardware, 
   as described in the :ref:`booting-and-installation` tech note.

.. _`Yocto Project Errors and Warnings`: http://www.yoctoproject.org/docs/current/mega-manual/mega-manual.html#ref-qa-checks
.. _`Yocto Project Quick Start: Building Images`: http://www.yoctoproject.org/docs/current/yocto-project-qs/yocto-project-qs.html#qs-building-images
.. _`Yocto Project: Working Behind a Network Proxy`: https://wiki.yoctoproject.org/wiki/Working_Behind_a_Network_Proxy


Image Configuration
===================

Building images depends on choosing the private keys that are needed
during the build process: you either generate and configure
these keys, or disable the features which depend on them. In some cases,
common configuration options are included but commented out and can
be enabled by removing the comment.

Images are locked down by default: for example, none of
the existing user accounts (including root) has a password set, so
logging into the running system is impossible. Before building an image,
you must choose a way of interacting with the system after it has booted.

.. NOTE: this section introduces the difference between development and production
   images first because it is a choice that must be made before building. Choosing
   architecture, image format and image content are more important than optional
   build tweaks (sstate, removal of old images), so those come last.


Development Images
------------------

All images provided by the Ostro Project are intended for
developers and not directly for production use. To avoid having developers
accidentally build images for real products that have development
features enabled, you must make explicit changes in ``local.conf`` to
enable them.

Developers building their own images for personal use can follow these
instructions to replicate the configuration of the published Ostro OS images. All necessary
private keys are provided in the ``ostro-os`` repository.

To do this, before building,  edit the :file:`conf/local.conf` configuration file,
find the line
with ``# require conf/distro/include/ostro-os-development.inc`` and
uncomment it. This will also add some recommended software to the ``ostro-image-noswupd``
reference image, see below for details.

By default, remote access via ssh is not permitted, but you can learn how to configure
Ostro OS to allow this in your development image in this :ref:`authorized-keys` tech note.

Production Images
-----------------

When building production images, first follow the instructions
provided in :file:`meta-intel-iot-security/meta-integrity/README.md` for creating your own
keys. Then edit the :file:`conf/local.conf` configuration file and
set ``IMA_EVM_KEY_DIR`` to the directory containing
these keys or set the individual variables for each required
key (see ``ima-evm-rootfs.bbclass``).

In addition, find the line
with ``# require conf/distro/include/ostro-os-production.inc`` and
uncomment it. This documents that the intention really is to build
production images and disables a sanity check that would otherwise
abort a build.

Then add your custom applications and services by listing them as
additional packages as described in the next section.


Target MACHINE Architecture
----------------------------

The build's default target architecture ``MACHINE`` is ``intel-corei7-64``, appropriate for the
MinnowBoard Turbot and GigaByte platforms, 
as configured in :file:`build/conf/local.conf`. 
You can edit the :file:`local.conf` file to change this to a different machine appropriate for your platform. 

For currently :ref:`platforms`, the appropriate ``MACHINE`` selections are:

.. table:: Yocto MACHINE selection for Supported Hardware platforms

    ==========================  ====================================
    Platform                    Yocto Project MACHINE selection
    ==========================  ====================================
    GigaByte GB-BXBT-3825       intel-corei7-64
    Intel Galileo Gen2          intel-quark
    MinnowBoard MAX compatible  intel-corei7-64
    Intel Edison                edison
    BeagleBone Black            beaglebone
    ==========================  ====================================

Virtual machine images (a :file:`.vdi` file) are created for the ``intel-corei7-64``  hardware platforms as part 
of the build process (and included in the prebuilt image folder too).


Image Formats for EFI platforms
-------------------------------

For EFI platforms, you can produce different types of images:

.dsk:
    The basic format, written to a block device to create a bootable image.

.dsk.vdi:
    VirtualBox* format, for running Ostro OS inside a Virtual Machine.

compressed formats:
    Same as above, only compressed, to reduce (final) space occupation
    and speed up the transfer between systems of the Ostro OS image.
    Notice that the creation of compressed images will require additional
    temporary space, because the creation of the compressed image depends
    on the presence of the uncompressed one.  (To save download time and
    server disk space, we only provide compressed images
    from http://download.ostroproject.org.)

    All compression methods listed for ``COMPRESSIONTYPES`` in
    ``meta/classes/image_types.bbclass`` are supported. In addition,
    Ostro OS adds support for compressing with :command:`zip`. ``xz``
    is recommended, while ``zip`` may be useful in cases where images
    have to be decompressed on machines that do not have :command:`xz`
    readily available.

To customize the image format, modify ``local.conf``, adding the variable
``OSTRO_VM_IMAGE_TYPES``, set to any combination of the following::

    dsk dsk.xz dsk.vdi dsk.vdi.xz

It will also trigger the creation of corresponding symlinks.

Example::

    OSTRO_VM_IMAGE_TYPES = "dsk.xz dsk.vdi.xz"

will create both the raw and the VirtualBox images, both compressed.


Base Images
-----------

In your cloned ``ostro-os`` repository folder, ``./meta-ostro/classes/ostro-image.bbclass``
contains the base definitions for building Ostro OS images. ``./meta-ostro/recipes-image/images/``
contains some example image recipes.

The ``ostro-image.bbclass`` can be used in two modes, depending on the ``swupd`` image feature:

* swupd active: produces a swupd update stream when building images and in
  addition defines virtual image recipes which produce image files that are
  compatible with that update stream.
* swupd not active: this is the traditional way of building images, where
  variables directly control what goes into the image.

Developers are encouraged to start building images the traditional way
by using image recipes like ``ostro-image-noswupd`` where swupd is
turned off and only use swupd during deployment.

That's because image creation based on swupd bundles and swupd bundle
creation itself cause additional overhead (disk space, compile time)
due to the extra work that needs to be done (creating multiple rootfs
directories to simulate what needs to be in each bundle, preparing the
data that the swupd client pulls via HTTP(S) when checking for
updates). This can increase the build time from several minutes to
over an hour or more (depending on the number of bundles and files).

The following instructions assume that swupd is not used.

.. TODO: document how to configure swupd once it is better understood
   and tested.

.. TODO: document how to create custom image recipes based on ostro-image.bbclass.


Installing Additional Packages without swupd
--------------------------------------------

``ostro-image.bbclass`` defines several image features which can be enabled
to install additional sets of components. For example, to install debugging
tools, compilers and development files for all components in the image, add::

    OSTRO_IMAGE_EXTRA_FEATURES += "tools-debug tools-develop dev-pkgs"

Extend ``OSTRO_IMAGE_EXTRA_INSTALL`` to install additional individual packages,
for example with::

    OSTRO_IMAGE_EXTRA_INSTALL += "strace"

Alternatively, ``CORE_IMAGE_EXTRA_INSTALL`` can also be used. The
difference is that this will also affect the initramfs images, which is
often not intended.

The example ``ostro-image-swupd`` is defined such that its default
content corresponds to ``ostro-image-noswupd``. It is possible to
reconfigure it so that it matches ``ostro-image-swupd-dev``::

    OSTRO_IMAGE_NOSWUPD_EXTRA_FEATURES_append = "${OSTRO_IMAGE_FEATURES_DEV}"
    OSTRO_IMAGE_NOSWUPD_EXTRA_INSTALL_append = "${OSTRO_IMAGE_INSTALL_DEV}"


Accelerating Build Time Using Shared-State Files Cache
------------------------------------------------------

As explained in the `Yocto Project Shared State Cache documentation`_, by design
the build system builds everything from scratch unless it can determine that
parts do not need to be rebuilt. The Yocto Project shared state code supports
incremental builds and attempts to accelerate build time through the use
of prebuilt data cache objects configured with the ``SSTATE_MIRRORS`` setting.

By default, this ``SSTATE_MIRRORS`` configuration is enabled in :file:`conf/local.conf`
but can be disabled (if desired) by commenting the ``SSTATE_MIRRORS`` line
in your :file:`conf/local.conf` file, as shown here:::

   # Example for Ostro OS setup, recommended to use it:
   #SSTATE_MIRRORS ?= "file://.* http://download.ostroproject.org/sstate/ostro-os/PATH"

 

.. _Yocto Project Shared State Cache documentation: http://www.yoctoproject.org/docs/2.0/mega-manual/mega-manual.html#shared-state-cache


Removing Previous Image to Save Disk Space
------------------------------------------

Every image built gets copied into the deploy directory. As you're developing,
these repeated builds will start accumulating and use up more and more
disk space. You can save disk space by removing previous images after the
new one is successfully built by adding (or uncommenting) this line in your
:file:`local.conf`: ``RM_OLD_IMAGE = "1"``
