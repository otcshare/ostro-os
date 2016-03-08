.. _system-and-security-architecture:


Ostro |trade| OS System and Security Architecture
#################################################

Introduction
============

The Ostro |trade| OS is a pre-compiled, configured and secured base
Internet of Things (IoT) Linux\* OS that supports creating custom images
easily. For more information, see :ref:`about_ostro`.

Because security is crucial for IoT, security mechanisms
are tightly integrated into the system architecture. The primary
customers for Ostro OS are considered to be OEMs, OSVs, Service
Providers, and developers building their own devices.

This document introduces key concepts in the Ostro OS and how they fit
together. The target audience is developers who want to learn about
Ostro OS or use the OS in their own product. Application
developers will also find this to be useful background information.
There will also be documentation more focused on application
development and installation.  The :ref:`Building Images` tech note
will also help get you started.


There is no “one solution that fits all” when
talking about IoT security. Thus, what Ostro OS provides are
(pre-configured) mechanisms and templates for supported use cases. The
recommended configuration is delivered pre-compiled, so building a
full disk image is fast. Less common configurations are still
possible, but may require compiling from source.

The expectation is that most devices will have just a few trusted
applications and not have access to an application store. Compared to,
say, a mobile phone OS, the security focus is moved from protecting
against malicious application to protecting against attacks coming
from outside the device (network or malicious physical
access). However, the security is planned to be scalable. If there is
a problem that the default security setup does not cover, the security
can be stepped up by adding components and configuration.

Supporting multiple real users of the same device is less
important and left to applications to support. Therefore the security
model can use Unix users to distinguish between different
applications. All interaction with the device is done
through applications, not by logging into the core system directly.

This architecture documentation explains how the security is currently
integrated into the Ostro OS. Especially covered are the
places where the security model differs from baseline Linux security
that can be expected from any mainstream desktop Linux distribution.

For a discussion of potential other security mechanisms see the
:ref:`security-threat-analysis` documentation.


Key Security Concepts
=====================

* Scalable Security: Protection mechanisms can be turned on to
  increase security (defense in depth) or turned off to decrease
  overhead and complexity. However, not all combinations are
  tested, see `Production and Development Images`_ later in this document.

* Unix DAC is used to separate applications. Each application runs
  under a different UID. Supporting multiple real users of the same
  device is left to applications to support.

* Permission checks are based on Unix group membership.

* When using DAC alone, applications can communicate with each
  other. Application authors must be careful about setting permission
  bits as intended to prevent that. Because applications are trusted,
  this is acceptable. When that is undesirable or to mitigate
  risks when applications get compromised, optionally Smack as a MAC
  mechanism can be used to separate applications further.

* Namespaces and containers further restrict what applications can
  access and do.

* An IPv4/IPv6 firewall controls access to local services.

* The core OS is hardened with a combination of suitable compiler
  flags, running services with minimal capabilities, and avoiding
  insecure configurations.

Boot Process + Secure Boot
==========================

1. The first stage is hardware specific. Currently supported is UEFI
   Secure Boot: Ostro OS installs the Linux kernel and initramfs
   combined into a single, signed UEFI blob. That blob gets loaded and
   verified directly by the device firmware. The following stages are
   the same for all devices.

2. The Linux kernel starts up and transfers control to the initramfs.
   The initramfs goes through several steps, the main ones being:

   a) it searches (and if necessary, waits) for the root partition

   b) when using IMA with EVM, and booting for the first time, it is
      necessary to personalize the EVM protection to the current
      device; more on that below.

   c) if used, IMA/EVM policy gets activated

   d) the file system root is changed to the root partition and
      control is transferred to system as PID 1

3. Systemd finishes bringing up the userspace side of the system.

4. Applications get started by systemd because they are also systemd
   service (see `Applications`_).

The chain of trust in Secure Boot cannot stop at the kernel. To
protect against offline attacks, all files loaded for booting the core
system must also be checked for integrity before using them. IMA/EVM
ensure that as follows:

* IMA hashes the content of the file and stores the hash in a
  security.ima xattr attached to the file’s inode. This hash can
  already be calculated on the build host for read-only files and be
  transferred to the device together with the file content, in which
  case it is possible to sign it with a secret private key.

* This is the most secure method: the kernel then checks the signature
  using a public key rooted in a CA that got compiled into the kernel
  and thus is anchored in the UEFI Secure Boot chain. Not even a root
  process can create new files with a valid signed security.ima xattr.

* The less secure approach is to allow file creation and have the
  kernel create the content hash on file closing. This mode is
  necessary for files which have to be created or modified on the
  device. It depends on the IMA policy where such files are accepted.

* EVM hashes inode meta data like protection bits and xattrs like
  security.ima and stores the hash in security.evm. The inode number
  is also included in the hashed data, to prevent copying security.evm
  from one inode to another. Because the update mechanism is file
  based, inode numbers vary between devices and therefore signing the
  EVM hash on the build host is impossible. Instead, the Ostro OS relies
  on a per-device secret key stored in a TPM, with a less secure
  software-only solution as fallback (see below). That key is used to
  encrypt and decrypt the EVM hash. Because the key is sealed in the
  TPM, even an attacker with physical access to the device and the
  root partition cannot access it, which makes it possible to detect
  offline attacks because files created or modified by an attacker
  with not have a security.evm that passes the runtime checks. The
  secret key needed for EVM is set up by the initramfs. This all
  happens automatically, without the need for user interaction.

* All files are checked on access and if the hashes does not match the
  current content or meta data, access fails with a “permission
  denied” error. When listing directories with files that do not pass
  the check, only the file names will be visible. Additional details
  that belong to the inode, like size or protection bits, cannot be
  shown because access to them gets denied.

* Without a TPM, Ostro OS falls back to software encryption keys for
  EVM. This still protects against online attacks (because the kernel
  can limit access to the secret key) but is not sufficient to prevent
  offline attacks.

.. _filesystem-layout:

Filesystem Layout
=================

The Ostro OS needs to protect data differently, depending on sensitivity
and usage patterns. Files used by the core system change infrequently
and can be protected by IMA/EVM. But IMA/EVM changes the performance,
semantic and error handling of the filesystem and thus is less
suitable for application data with unknown usage patterns.

Here is an overview of the different parts of the virtual file
system. Specific devices will likely map this to different
partitions because that way the filesystem UID can be used in the IMA
policy to treat files differently depending on their
location. However, a simpler Ostro OS configuration could also drop
IMA and use a simpler partition layout where everything is stored in
the same writable partition.


``/``
  Includes everything that is not explicitly listed
  below. Conceptually this is read-only and will only be mounted
  read/write during system software updates Currently / is mounted 
  read/write all the time but all services
  except software update use systemd's ``ProtectSystem=full`` to make the
  root filesystem appear read-only to them. The goal is to have all files 
  signed using IMA hashes. The IMA policy may be updated in future builds
  to provide a clean separation
  between read-only and read/write files in different partitions.

``/var``
  Persistent data which can be written on the device. Protected by
  IMA/EVM with hashes created on-the-fly by the kernel on the device.

``/tmp`` and ``/var/run``
  A tmpfs which will not survive a reboot.

``/home``
  Persistent, read/write, no IMA/EVM. Each application gets its own
  home directory with access limited to the application.

``/etc``
  The files in it are part of the core OS and thus considered
  read-only. However, there are a few noteworthy exceptions:

``/etc/ld.so.cache``
  Its content depends on the currently installed shared libraries,
  which may vary by device. In future builds it will be updated on the
  device after system software installation or updates. 

``/etc/machine-id``
  Currently systemd creates a machine ID when booting and writes it to
  ``/etc/machine-id`` when ``/etc`` becomes writeable. In future builds
  this can be updated as per the IMA policy. 


User, Group and Privilege Management
====================================

User and group management files (like ``/etc/passwd``) are
read-only. That means that the core system can only have static system
users. It is not possible to set a root password.

To become root in the core system:

* After installation and before booting for the first time, add a
  public key to the ``~root/.ssh/authorized_keys`` file.

* \*In the development image\*: log in via a local console or
  serial port as root. A PAM module allows root to log in without a
  password. The development and production image use different
  signing keys so PAM module and its configuration cannot be
  copied from a development image to a production image.

Most groups are used to control access to certain resources like
files, devices or privileged operations in system daemons. Device node
ownerships are set using udev rules, similar to how ``audio`` and
``video`` are handled in traditional Linux desktop systems.


Process Handling
================

Directly after booting, systemd as PID 1 is the only running
process. Nothing potentially started in the initramfs survives.

All processes are started by systemd, including
applications. systemd’s interfaces (``systemctl`` and the `D-Bus API
of systemd`_) are the currently supported interfaces for listing and
controlling processes.

.. _`D-Bus API of systemd`: http://www.freedesktop.org/wiki/Software/systemd/dbus/


Applications
============

At the moment, applications are only supported when built
into the image (“pre-installed applications”) installed on a
device. Such applications can use the normal Yocto Project configuration
tools for creating
the user they run under, install files in the normal root file system,
cause additional system packages they depend on to be added to the
image, etc.

What distinguishes applications from regular system services is that
they provide a manifest file which defines how to start them. In other
words, applications on Ostro OS are essentially system services, they
just get installed differently.

That manifest file is translated by the
application framework in Ostro OS into a systemd service file
(``/run/systemd/system/app-$ID.service``). The long-term goal is to limit
where applications can install files and rely exclusively on the
application manifest file.

The generated systemd service file contains settings that are used to
isolate the application from other applications. In a system that runs
with only basic Unix DAC, every application is run as a different user
and the user can belong to different Unix groups. These groups specify
the access the application will have to different system resources. As
applications run as different Unix users, ptrace-based attacks are
prevented.

For more information about the application framework and the manifest
content, see :ref:`application-framework`.

Since applications are run with different user accounts but MAC is
optional, applications can arrange to share data between themselves in
some cases when they are running outside of containers, inside the
same container, or when the containers do not isolate IPC or network
namespaces. The applications can, for instance, use abstract Unix
domain sockets, loopback network interface, or System V message queues
for connecting to each other. Note that this behavior is not as such
encouraged or documented by the Ostro OS -- it’s just not explicitly
disallowed. If the system integrator wants to prevent this behavior,
using MAC or containers for application isolation is recommended.

Applications provide the main interface to a device and thus have
higher exposure to attacks than the OS itself. It is recommended that
application providers perform strong application validation and run
applications with minimal privileges and strong separation from the OS
and other applications. Guidelines for that will be published later.


System Updates
==============

Ostro OS binaries are delivered as bundles, as in the Clear Linux OS.
Bundles are a bit like traditional packages, but can overlap with
other bundles and come with less metadata. 
There is a core bundle with all the
essential files required to boot the system. Several optional bundles
contain individual runtimes and applications that were built together
with the OS.

Installing bundles must not change files contained in other bundles,
i.e., if a file is contained in more than one bundle, it must have
exactly the same content and attributes in all those bundles. So
conceptually, one can imagine the bundle creation as installing all
components of the OS in an image, configuring the image and then
splitting up the installed files and their attributes as found in that
image (for example, the signed security.ima xattr) into different
bundles according to some policy (core OS bundle, application bundles
where each bundle contains the application and all non-core files it
depends on).

When compiling a new revision of the OS, new bundles and binary deltas
against older revisions of the bundles are calculated and published on
a download server. The Clear OS swupd tool is then responsible for
downloading the deltas and applying them to the local copy of the
bundles.


Core OS Hardening
=================

In future builds, these additional features will be considered for Core OS hardening:

- noexec tmpfs mounts
- running daemons as non-root (e.g., ambient capabilities, rfkill group for connman)
- dealing with services needing to talk with each other, D-Bus policies etc.
- systemd options for services.


Network Security
================

Firewall design
---------------

Ostro OS has a firewall that out-of-the-box protects the system services using
both IPv4 and IPv6. The applications and services need to open holes into the
firewall if they require to be accessible from the network, that is to offer
services to the network. If the device running Ostro OS is meant to be an
Internet gateway or otherwise have a complex network setup, the system
integrator has to change the initial firewall ruleset.

Currently the firewall rules are composed of three parts:

1. The initial default ruleset, loaded with ``iptables-restore``
2. Service-specific rules, set from systemd configuration files using
   ``iptables`` and ``ip6tables``, loaded when the service is started
   and unloaded when the service is stopped
3. Application-specific rules, set either from systemd configuration
   files or by container launcher (such as ``systemd-nspawn``)

At the moment there is no abstraction layer for the first two cases. The default
ruleset needs to be set in ``iptables-restore`` compatible format and the
services must use ``iptables`` and ``ip6tables`` commands for punching holes to
the firewall and doing any other firewall configuration they might require.

An example systemd socket extension file for opening IPv6 firewall port
for sshd (this file is
``/lib/systemd/system/sshd.socket.d/openssh-ipv6.conf``):

::

  [Unit]
  After=ip6tables.service

  [Socket]
  ExecStartPre=/usr/sbin/ip6tables -w -A INPUT -p tcp --dport ssh -j ACCEPT
  ExecStopPost=/usr/sbin/ip6tables -w -D INPUT -p tcp --dport ssh -j ACCEPT

The ``-w`` switch is needed to both ``iptables`` and ``ip6tables`` commands to
prevent race conditions with firewall locking.

Current approach lets the firewall rules to be simple, and the writers of the
service rules can use the extensive documentation available for iptables
toolchain to write, debug, and verify the rules. Also, the iptables toolchain
provides the system integrator the possibility to do almost any firewall setup
imaginable, letting Ostro OS to be future-proof in this regard.

Firewall default configuration
------------------------------

The default Ostro OS firewall configuration is a restrictive one. Briefly, all
incoming packets are dropped, except for those belonging to already established
connections or those that are coming from the loopback interface. Forwarding
packets is not allowed. All outgoing packets are accepted. In addition to this,
the IPv6 firewall is configured to accept incoming ICMPv6 packets.

System services are not supposed to change the fundamental way the firewall is
set up. They are meant to configure the firewall so that they can function
properly, but the firewall settings they do must not compromise the firewall
security or interfere with the operation of other services or applications.
Ostro OS does not have a centralized firewall control, so the service writers
must be careful about this.


Production and Development Images
=================================

By default, building an image results in something that is locked-down
and secure. This is how real products should be built. Unless some
kind of application gets installed during image creation, one cannot
do much with the running image (no user interface, no way to log into
the system).

During development, a more open image is more useful. The Ostro project
contains a ``ostro-os-development.inc`` file that can be included
in a build configuration's ``local.conf`` to produce "development"
images.

*IMPORTANT*: such development images are intentionally not built to be
perfectly secure! Do not use them in products built for end-customers and
use them only in secure environments.


The Ostro Project provides two different pre-compiled images,
``ostro-image`` and ``ostro-image-dev``. Despite the name, currently *both*
are compiled as development images. The only difference is that
``ostro-image-dev`` already includes development (``gcc``) and debugging
tools (``strace``, ``valgrind``, etc.). There are no pre-compiled
production images.

The following table summarizes the differences between the default
configuration for production images and images built with
``ostro-os-development.inc``:

============================= ================================ ==========================================
\                             production image                 development image
============================= ================================ ==========================================
Target audience               End-customers                    Developers
----------------------------- -------------------------------- ------------------------------------------
Usage                         Reference platform for products  Experimenting with Ostro OS, developing
                                                               Ostro OS or applications
Kernel                        Production kernel                Development kernel
IMA signing key               Product-specific, secret         Published together with the Ostro OS
                                                               source code
swupd signature validation    TBD
----------------------------- ---------------------------------------------------------------------------
Kernel debug interfaces       Disabled                         Enabled 
Root password                 Not set
----------------------------- ---------------------------------------------------------------------------
Local login as root           Disabled                         Enabled for console (tty) and serial port,
                                                               automatic login
SSH                           Installed, but disabled          Installed and running, but authorized keys
                                                               must be set up before it becomes usable
============================= ================================ ==========================================

For more information about signing, see the :ref:`certificate-handling` how-to tech note.


Privacy Design
==============

By itself, Ostro OS collects and stores very little information
related to the user of a device.

In production and development images, connman stores information about
LANs and WLANs that were seen or connected to under ``/var/lib/connman``.  On
development images, developers can enable remote
access via ssh by creating a ``/home/root/.ssh/authorized_keys`` file
and can also store arbitrary additional information under ``/home``.

This private information is protected against offline modifications as
explained in :ref:`filesystem-layout`. However, that protection is
still limited and there is no protection against offline read
access.

Most of the information about the user will be collected and stored by
applications. It is the responsibility of the application developers
to protect that information.

Encryption support in the base Ostro OS like whole-disk encryption
will be added in the future to protect files at the OS level. Currently, 
applications can use the normal cryptographic libraries available
on Linux to encrypt data before storing it in files. These applications
also need to implement their own key handling when doing that.

A device gets a unique ID when it boots, stored persistently under
``/etc/machine-id`` by systemd. Applications can use that identifier
when communicating with other devices or services. The OS itself only
uses it internally. A device and indirectly the user can also be
identified by the device's LAN and WLAN MAC addresses. Ostro OS
provides no mechanism to obscure those.
