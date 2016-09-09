This README file contains information on the contents of the
security-framework layer.

Please see the corresponding sections below for details.


Dependencies
============

This layer depends on:

    URI: git://git.openembedded.org/bitbake
    branch: master

    URI: git://git.openembedded.org/openembedded-core
    layers: meta
    branch: master


Patches
=======

Please submit any patches against the security-framework layer via
Github pull requests.

For discussion or patch submission via email, use the
yocto@yoctoproject.org mailing list. When submitting patches that way,
make sure to copy the maintainer and add a "[meta-intel-iot-security]"
prefix to the subject of the mails.

Maintainer: Patrick Ohly <patrick.ohly@intel.com>


Table of Contents
=================

  I. Adding the security-framework layer to your build
 II. Misc


I. Adding the security-framework layer to your build
====================================================

In order to use this layer, you need to make the build system aware of
it.

Assuming the security repository exists at the top-level of your
yocto build tree, you can add it to the build system by adding the
location of the security-framework layer to bblayers.conf, along with any
other layers needed. e.g.:

  BBLAYERS ?= " \
    /path/to/yocto/meta \
    /path/to/yocto/meta-yocto \
    /path/to/yocto/meta-yocto-bsp \
    /path/to/yocto/meta-intel-iot-security/meta-security-smack \
    /path/to/yocto/meta-intel-iot-security/meta-security-framework \
    "

II. Misc
========

Some components in this layer (like e2fsprogs or keyutils) are
general-purpose tools or extensions which are needed when using Smack or
integrity protection.
