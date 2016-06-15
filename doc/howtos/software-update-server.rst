.. _software-update-server:

Software Update: Building an Ostro |trade| OS  Repository
#########################################################

This technical note provides instructions for creating
a repository used for updating devices based on Ostro OS.

Prerequisites
=============

- **Additional (fast) disk space**: the SW Update tool is provided as
  an additional layer, therefore it doesn't require any additional
  element.
  The process of generating the bundles and updates can be very
  disk intensive and dramatic speed improvements can come from
  using a fast disk storage system, including use of SSD and RAID
  arrays.
  An execution round will also produce various rootfs directories
  as intermediate artefacts.
  The actual disk footprint depends on the bundles selected and
  defined and will be larger than that produced by a simple typical
  distribution build based on OECore or Yocto Project.
- **Signing keys** (alternatively testing keys from the :file:`swupd-server`
  project can be used).

Bundles definition
==================

The documentation for using SW Update in Yocto Project can
be found in the `swupd layer`_ and is only summarized here.
These instructions assume that the work will happen on top of an
image flavor that has swupd enabled, for example by building an image,
such as with::

   $ bitbake ostro-image-swupd

or by downloading a pre-compiled image with ``-swupd`` in its name
from the `Ostro OS download server`_

.. _`Ostro OS download server`: https://download.ostroproject.org

These are the main steps:

#. Optionally, in ``conf/local.conf`` or equivalent location, set the
   `OS_VERSION` variable to an integer value.
   If set explicitly, this number must be increased before each build
   that generates swupd update artefacts.

#. Assign a list of bundle names to ``SWUPD_BUNDLES``::

     SWUPD_BUNDLES = "feature_one feature_two"

#. For each named bundle, setup a varflag of ``BUNDLE_CONTENTS``
   that matches the bundle name, and initialize it with a list of
   packages whose content must be included in the bundle::

     BUNDLE_CONTENTS[feature_one] = "package_one package_three package_six"

Creating a Custom Image and matching Software Update Repository
===============================================================

Some of the steps listed in this section are optional and cover
advanced configuration functionality that's only needed
if the default configuration of
the Ostro OS already meets your needs.

The process is exemplified by using real components and describing
what each step looks like when applied to such components.
Unless stated otherwise, the changes described are made in
the ``conf/local.conf`` file.


Step 0: Review and optionally modify the content of the os-core bundle
----------------------------------------------------------------------
The ``os-core`` bundle comes with a predefined set of components,
however each device is likely to have slightly different requirements.
In some cases it might be necessary to adjust the set of components
included in ``os-core``.

To do this, either modify or extend the ``OSTRO_IMAGE_FEATURES_REFERENCE``
and the ``OSTRO_IMAGE_INSTALL_REFERENCE`` variables for changes
respectively to the feature and component sets.

We're modifying ``os-core`` because it's the only unremovable bundle and is
therefore well suited to deliver tools
that must always be available to your devices. For many IoT products,
the actual application would be added to ``os-core`` like this.

For example, you can add the content of the ``sudo`` recipe to the 
``os-core`` bundle by adding this line to your ``local.conf`` file::

  OSTRO_IMAGE_INSTALL_REFERENCE += "sudo"

Adding recipes this way works only for adding components to ``os-core``
and is the typical case when customizing Ostro OS, because the
``os-core`` is a minimal configuration.

However, if you need to remove something from ``os-core``,
you'll create either a new image recipe or a new
``.bbappend file``, where you'll modify the variables that define the
content of ``os-core``.

These are the variable that must be modified::

* OSTRO_IMAGE_FEATURES_REFERENCE
* OSTRO_IMAGE_INSTALL_REFERENCE
* IMAGE_INSTALL

We recommend you modify a copy of the original recipe
``ostro-image-swupd.bb`` and refer to ``ostro-image.bbclass``
for the values to use.


Step 1: Review and optionally modify the list of bundles
--------------------------------------------------------
Ostro already defines some bundles, and users can define additional ones.

Example::

  SWUPD_BUNDLES += "sudo_bundle"
  BUNDLE_CONTENTS[sudo_bundle] = "sudo"

This example is an alternative way to add the component shown in
Step 0 above, but has an important difference.  Instead of extending 
the content of ``os-core``, this alternative way put the extra
component in its own bundle and will not install the component by default 
in any image.


Step 2: Review and optionally modify the content of the images created
----------------------------------------------------------------------
It is also possible to choose which bundles will be pre-installed on the
customized image, by:

#. Adding a new item to the list of buildable images, and list the
   bundle(s) desired.

   Example::

     SWUPD_IMAGES += "\
       pre_installed_content \
     "

#. Defining the content of the new buildable image (the image with the
   pre-installed bundles, from the previous point), by adding a varflag
   to SWUPD_IMAGES that enumerates the bundles to pre-install.

   Example::

     SWUPD_IMAGES[pre_installed_content]="\
       sudo_bundle \
       add_here_other_bundles_if_needed \
     "

   ``SWUPD_IMAGES`` is the only token which is specific to the Ostro OS
   syntax. The other identifiers are under the developer's control.


This will add a new image option called
``ostro-image-swupd-pre_installed_content``
to the set of images that are buildable. This new image
contains the
``os-core`` bundle,  the ``sudo_bundle`` bundle from Step 1, and whatever
else might have been added.

If you have ``sudo`` as part of ``os-core``, then you:

* remove it from the bundle and publish the update, *all* the devices will have sudo removed.
* add it to the bundle and publish the update, *all* the devices will have sudo installed.

If you have ``sudo`` as ``sudo_bundle``, then you do not automatically install or remove 
that in any device. You make it available and have an option to be installed or not on each device.

Put another way, the purpose of using a bundle is to allow a feature to be installed 
or removed *per device* or
an application that one user may want while another may not. 
For example, a security system device may optionally install the UPnP/DLNA media provider to access
the recorded files, while a drone device could have a "camera" bundle installed containing the kernel module (v4l),
media pipeline (gstreamer) and a server to stream it.

Compared to the approach taken in Step 0, 
this approach allows you to remove the content of the bundle without having to
create an update (and thus a new release).

.. note::
   Each defined bundle generates an additional workload when
   building images and SW Update repositories so we recommend
   you enable only those bundles that
   are effectively useful for the specific use-case targeted.

Products should override the set of predefined default bundles that come
from Ostro OS, by editing the
``SWUPD_BUNDLES`` variable.  Doing so will discard anything that was 
part of the Ostro OS defaults;
if any of the pre-defined bundles are still needed, they must be 
explicitly listed again.

Example::

   SWUPD_BUNDLES = "sudo_bundle"



Step 3: Build the images and the SW Update repositories
-------------------------------------------------------

The typical command for generating the basic Ostro OS image and related
SW Update stream is::

 $ bitbake ostro-image-swupd

However, if one wants to have pre-installed bundles, then the command
must refer to the specific variant.

Example (Continuing from Step 2)::

  $ bitbake ostro-image-swupd-pre_installed_content

Assuming that the chosen architecture defined in ``local.conf`` was ``intel-corei7-64``, 
the yield from the command in the example is:

* The image with the chosen pre-installed bundles::

    tmp-glibc/deploy/images/intel-corei7-64/ostro-image-swupd-pre_installed_content-intel-corei7-64.dsk

* The base image::

    tmp-glibc/deploy/images/intel-corei7-64/ostro-image-swupd-intel-corei7-64.dsk

* The work directory for generating SW Update repository::

    tmp-glibc/deploy/swupd/intel-corei7-64/ostro-image-swupd/

*  This folder contains both data from intermediate steps and the actual
  SW Update stream located here::

    tmp-glibc/deploy/swupd/intel-corei7-64/ostro-image-swupd/www/

This folder will also contain data related to subsequent builds and
must be exposed through a web server (e.g., ``nginx`` or ``apache``)
to the device running the SW update client for getting its maintenance.


Step 4: Create an update from the previous step
-----------------------------------------------

Continuing with the previous example, one possible enhancement is to add a
new bundle, or modify the content of
the existing bundle(s).

To keep the execution simple, our example bundle will contain only one component
currently missing from the, for example, "Version 10" of the distribution: the
``sed`` command.

The changes required are:

#. Bump the version number::

     OS_VERSION = "20"

#. Add the new bundle to the list of bundles::

     SWUPD_BUNDLES += "sed_bundle"

#. Define the content of the newly created feature::

     BUNDLE_CONTENTS[sed_bundle] = "sed"

#. Had it been required to have the bundle pre-installed, it would have
   been added to the list of pre-installed bundles::

     SWUPD_IMAGES[pre_installed_content]="\
       sudo_bundle \
       sed_bundle \
     "

   But it's not required in this example, so we'll skip this step.

Finally, to generate the desired artefacts, the build command must be
run again::

    $ bitbake ostro-image-swupd-pre_installed_content

The yield is similar to the previous invocation, however now it also  
contains the SW Update data for the newly defined bundle containing ``sed``.

Because ``sed`` was introduced in the build ``Version 20``, devices that
are using earlier versions will not have access to this bundle. 
Such devices must first upgrade to a version where the bundle is
available and only then, they can install the new bundle.

.. _`swupd layer`: http://git.yoctoproject.org/cgit/cgit.cgi/meta-swupd/tree/docs/Guide.md
