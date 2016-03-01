.. _security-threat-analysis:

Ostro |trade| OS Security Threat Analysis
##########################################

Introduction
============

The Ostro |trade| OS security model aims to utilize standard components,
be simple and easy to understand, and allow extensibility and
scalability. Our focus is more
on protecting the IoT device from network attacks and less on
protecting against malicious users and application developers.

Document Scope
--------------

This document defines the main security threats and our solutions to
them. It also describes additional security mechanisms that can be
used for device types that have different requirements.

For a more general introduction to Ostro OS and its architecture see
the :ref:`system-and-security-architecture` document.


Glossary
--------

Here are some terms used within this document.

========== =============================================
 Acronym   Description
========== =============================================
IOT        Internet of Things
OS         Operating System
DAC        Discretionary Access Control
MAC        Mandatory Access Control
CVE        Common Vulnerabilities and Exposures
API        Application Programming Interface
(N|H)IDS   Network or Host Intrusion Detection System
IMA        Integrity Measurement Architecture
IP         Internet Protocol
CPU        Central Processing Unit
NFC        Near Field Communication
USB        Universal Serial Bus
WAN        Wide Area Network
(W)LAN     (Wireless) Local Area Network
TLS        Transport Layer Security
URL        Uniform Resource Locator
TPM        Trusted Platform Module
OEM        Original Equipment Manufacturer
========== =============================================

Security Principles
===================

There is no "one
solution that fits all" when talking about IoT security. 
Devices using the Ostro OS will vary greatly depending on their 
planned use, and there
will be many Ostro OS use cases that we cannot even see yet. 
Devices may also have secondary and tertiary use cases outside of their
originally planned environment. Thus, we will provide
(pre-configured) mechanisms and templates for supported use cases and
help our customers provide systems with maximum security
and minimum hassle.

Most IoT devices will have just a single application and not have
access to an application store. This is also the use case that Ostro OS
security is optimized for. Compared to say, a mobile phone OS, the
Ostro OS security focus is moved from application security to network
security. However, the security is planned to be scalable. If there is
a problem that the default security setup does not cover, the security
can be stepped up by adding components and configuration.

In addition, supporting multiple real users of the same device is less
important and left to applications to support. Therefore the Ostro OS security
model can use Unix users to distinguish between different
applications.

The Ostro OS will also provide clear documentation on how the security is
done and how it is expected to be extended or scaled. Especially
covered are the places where the security model differs from baseline
Linux security that can be expected from any mainstream desktop Linux
distribution.

Extensions to the support included in the
Ostro OS itself is also listed, primarily to document which additional
methods were also considered and excluded from the Ostro OS scope. If
desired, an OEM can add these additional methods, for example by
recompiling or reconfiguring the Ostro OS, but the Ostro OS itself will not provide
additional hooks for all of them.


Top-Level Security Challenges
=============================

Adversaries
-----------

..
  First column is necessary because the first column in a simple table may only have one line,
  and "Persona" is typically too long.

======= ================== ======================= ====================== ========== ==============
\       Persona            Motivation              Attacker type          Starting   Skill and
                                                                          privilege  potential
                                                                          level      effort level
======= ================== ======================= ====================== ========== ==============
\       Ostro OS           Damage vendor's         Network adversary      Low        High
        download and       brand;
        update             personal
        infrastructure     reputation;
        attacker           access to user
                           data and device
\       Authorized device  Override behavior       Local physical access  Medium     Medium
        user               defined by the
                           service provider
\       Malicious          Steal the physical      Local physical access  Low        Varies
        unauthorized       device or data in
        device user        it
\       Network attacker   Access to user data     Network adversary      Low        Varies
        (MITM attacker,    and device;
        script kiddie,     reputation
        botnet owner,
        etc.)
\       Authorized         Insider who wants to    Authorized adversary   High       Low
        malicious project  harm
        team admin
\       Malware developer  Access to user data     Local, non-physical    Medium     High (code
                           and device; reputation  access (application               injection),
                                                   intentionally gets                Medium (app
                                                   installed or code                 developer)
                                                   injected into the
                                                   device
======= ================== ======================= ====================== ========== ==============

Assets
------

========================== ====================== ============= ==================================== =============
Group                      Description            Business      Who should have access (Trust Model) Attack Points
                                                  impact if
                                                  compromised
                                                  (worst case)
========================== ====================== ============= ==================================== =============
Sensor data and actuators  Microphone, camera,    High          System components and applications   Device
                           temperature, heating                 according to their manifest
                           control, lighting ...                privileges

Application data           Log files, stored      Medium        Individual applications              Device
                           sensor data, media
                           files, application
                           credentials/keys
System data and files      credentials/keys,      Medium        System components (read/write),      Device
                           service configuration,               applications (read-only)
                           executables and
                           libraries
Access                     Privileged API         Medium        System components and applications   Device
                           access                               according to their manifest
                                                                privileges
Releases and tools         Ostro OS releases      Medium        Release manager, developers          Hosting
                                                                                                     web sites
Local network              UPnP protocol,         Medium        Authorized users and applications    Device
                           other devices
Device resources           CPU, memory, disk      Medium        Applications and system components   Device
                           space
========================== ====================== ============= ==================================== =============

The "Attack Points" column distinguishes between assets accessed
through the device (and where Ostro OS itself must protect the
assets), and other assets (where mitigation must happen elsewhere).


Attack surfaces
---------------

================================================ ============================ =================== =================
System Element                                   Compromise Type(s)           Assets exposed      Attack Method
================================================ ============================ =================== =================
Ostro OS update mechanism and servers            Data modification            System files        Network attack
Ostro OS installation                            Data modification            System files        Physical or
                                                                                                  network attack
User device (file system, databases)             Data modification,           Application and     Physical access,
                                                 elevation of privilege       system data         malware
Applications and services running on user device Elevation of privilege       Application and     Malformed input,
                                                                              system data         man-in-the-middle
Cloud service, other trusted devices             Data modification            Application and     Attack on the
                                                                              system data         remote device
                                                                                                  or service
================================================ ============================ =================== =================

Threats
-------

===== ================== ===================== ======================================================================
Name  Adversary          Asset                 Attack method and pre-conditions
===== ================== ===================== ======================================================================
Lib-1 Malware developer/ System code and files Exploiting a local or remote vulnerability in privileged Ostro OS code
      Network attacker
Lib-2 Malware developer/ Application data      Exploiting a local or remote vulnerability in an application or
      Network attacker                         Ostro libraries the application uses

Lib-3 Network attacker   Application data,     Pre-condition: attacker is able to upload a binary or runnable code
                         sensor data, system   to the system. Method: attacker executes a malicious binary or
                         data                  runnable code in the system
Lib-4 Network attacker   System data           An attacker can access the device when it's being provisioned
                                               (taken into use) because of insecure network provisioning or
                                               insecure default configuration
Lib-5 Download and       Releases and tools    Attacker has managed to compromise an Ostro OS update server
      Infrastructure
      attacker
Lib-6 Authorized device  System data,          Authorized or unauthorized user interferes with device boot and
      user / Malicious   application data      operation
      unauthorized
      device user
Lib-7 Authorized device  System data           Attacker reverts platform software to an earlier version that
      user                                     contains vulnerable software
Net-1 Network attacker / Local network         A malicious or compromised application or service threatens the
      Malware developer                        internal network
Net-2 Network attacker   Application / system  Man-in-the-middle attack
                         / sensor data going
                         over the network
Net-3 Malware developer  Sensor data           An Ostro OS-based network gateway is configured to collect sensor
                                               data, but a networked sensor bypasses the gateway to transmit
                                               data directly to Internet
App-1 Malware developer  Application data      A malicious or compromised application reads another application’s
      / Network                                private data or wants to kill or debug another application
      attacker
App-2 Malware developer  Device resources      A malicious or compromised application consumes all CPU, disk
      / Network                                space or memory
      attacker
App-3 Malware developer  Access; sensor data   A malicious or compromised application tries to access a sensor
      / Network                                or actuator that it has no right to access
      attacker
API-1 Malware developer  System or             Pre-condition: attacker is able to upload a binary or runnable code
                         application data      to the system. Method: use kernel interfaces for privilege
                                               escalation
API-2 Malware developer  System data           Unauthorized access to middleware APIs
API-3 Malware developer  Application data      Application misrepresents another application towards cloud
===== ================== ===================== ======================================================================

Threat details and mitigation
=============================

Lib-1
-----

*Threat*:

 A security bug is discovered in an Ostro component that runs with
 privileged access.

*Solution*:

 The most important thing is getting the security bug fix to the
 client devices as quickly as possible. We need to set up a
 process for tracking CVEs. If an upstream bug fix doesn’t get to
 oe-core or is otherwise delayed, we need to do the fix directly in the
 Ostro OS. The security fixes need to be communicated quickly to the
 customers, so that they will understand the real impact of the
 problem. The Ostro component selection should be partially based on
 the component security track record. This means we should avoid
 components with slow bug fix times or a history of security
 incidents, if possible.

 To mitigate the risk we should reduce the amount of privileged code
 that is run in the system. We should make sure that we are running a
 minimal configuration of a privileged service, disabling unused
 plugins and extensions and using a conservative service
 configuration. If possible, the system services should isolate the
 parts that need privileged access to a separate sub-component and run
 the rest of the service as user privileges. Systemd can be used to
 drop unneeded capabilities, thus limiting the potential damage. For
 services which don’t need admin capabilities, Systemd can also be
 configured to prevent service from accessing ``/home``, ``/root``, and
 ``/run/user`` by setting ``ProtectHome=true``, thus protecting user data. In
 addition, systemd ``ProtectSystem=full`` should be used to mount ``/usr``
 and ``/etc`` read-only when possible.

 Select the outward facing services carefully. Use well-tested
 libraries, have sensible configuration for services, pay attention to
 the security history, and try to write little custom code.

*Extensions*:

 Use a HIDS to detect intrusions in the system. An example of such a
 tool is Samhain (http://www.la-samhna.de/samhain/) or even IMA with
 log file monitoring. In case of a detected intrusion, reboot the
 device to a predefined fault target, which can for example restore
 the device to factory settings or alert the user.

 Use systemd’s support for service-private ``/tmp`` directory.

 Investigate Yocto Project support for various build-time security mechanisms,
 such as position-independent executables, FORTIFY_SOURCE, address
 space layout randomization, and glibc heap protector. Allow these to
 be turned on or off, depending on the performance characteristics of
 the system in development.

 Use MAC for giving system services more fine-grained access to system
 files.

 Test the selected Ostro OS network services with fuzzing and static
 analysis to find the bugs.

Lib-2
-----

*Threat*:

 An application needs to provide services to the network, opening an
 attack channel to the system.

*Solution*:

 To prevent the attack, limit access to services with a firewall. This
 allows the system administrator to make it possible to connect to the
 system by only a limited IP address range, for example. Limit what
 the applications can do by using access control mechanisms, such as
 Unix groups, for accessing platform features.

 Only enable required network protocols and avoid using networking
 protocols that do not include security mechanisms.

Lib-3
-----

*Threat*:

 Attacker is able to upload a binary or runnable code to the system.

*Solution*:

 Mount root filesystem read-only to prevent easy installation of
 malicious binaries there. Set the data partition and tmpfs to have a
 noexec flag. Use code signing (IMA) to verify binaries.

 For interpreted languages the situation is bit more
 complex. Interpreted languages are not affected by noexec, since the
 interpreter will generally reside in the root filesystem. They need
 to do the required changes inside the interpreter, so that running
 unsigned scripts is not allowed. The script signatures must be
 checked by the runtime. Especially code downloaded from Internet (by
 importing it directly or downloading it from the script) must not be
 ever run if a corresponding cryptographic signature does not
 validate.

Lib-4
-----

*Threat*:

 An attacker can access the device running the Ostro OS when it’s being provisioned
 (taken into use) because of insecure network provisioning or insecure
 default configuration.

*Solution*:

 Support key management through USB and NFC physical access
 methods. This can be done by providing first-boot network
 configuration authentication by using the URL returned by NFC. URL
 parameters contain the authentication token. For provisioning by
 starting the device in WLAN access point mode, use a generated
 device-unique key, which is provided as string or QR-code.

*Extensions*:

 The configuration can also be pulled from a pre-configured cloud
 service using a special token that is added to the device during
 production and is accessible from software.

Lib-5
-----

*Threat*:

 Attacker has managed to compromise an Ostro OS update server.

*Solution*:

 Clear Linux\* update mechanism (also used by the Ostro OS) signs each file, so updater sees if the
 files have been tampered with.

*Extensions*:

 Notification mechanism. If swupd is used wrapped in Soletta, it will
 report back to the caller about the error. The caller must then
 notify the user or do other appropriate actions based on
 pre-configured policies, such as changing the update mirror.

Lib-6
-----

*Threat*:

 Authorized or unauthorized user interferes with device boot and
 operation.

*Solution*:

 Secure Boot

Lib-7
-----

*Threat*:

 Attacker reverts platform software to an earlier version that
 contains vulnerable software.

*Solution*:

 Software update must not allow going backward in version numbers. In
 case of factory reset, the device should attempt to upgrade itself to
 the latest version available before exposing services to the network.

Net-1
-----

*Threat*:

 A malicious or compromised application threatens the internal network.

*Solution*:

 Use a firewall to filter access to the network. It’s possible to tag
 IP packets belonging to a certain user (iptables --uid-owner
 $UID). Configure firewall to give the application access only to the
 IP ranges that it needs to access. If the application runs in a
 container, the application will have a virtual interface in the
 container and the host can control routing packets from the interface
 with the firewall.

 systemd’s ``PrivateNetwork=yes`` can completely disable network access
 when it is not needed.

*Extensions*:

 Use MAC-based network labeling.

Net-2
-----

*Threat*:

 Attacker is disguised as a trusted resource outside the device running the Ostro OS.

*Solution*:

 Support DNSSEC to avoid cache poisoning and man-in-the-middle
 attacks. Utilize TLS 1.2 and device side certificates, and include
 support for client certificates. Support OAuth, Kerberos 5 and other
 multi-party authentication and authorization mechanisms.

 Certificate management (including certificate revocation) needs to be
 supported.

*Extensions*:

 Have a notification mechanism to tell the user when a remote
 certificate issue is found. Define customizable policies on what to
 do in this case.

Net-3
-----

*Threat*:

 An Ostro OS-based network gateway is configured to collect sensor data,
 but a networked sensor bypasses the gateway to transmit data directly
 to Internet.

*Solution*:

 Proper sensor provisioning helps to prevent accidental sending of
 data to the network. The Ostro OS is not by default preventing sensors from
 accessing the Internet.

*Extensions*:

 Configure firewall to block access of certain protocols that are
 often used to access IoT services (CoAP, MQTT). Prevent access to the
 data gathering addresses of well-known cloud services. Note that if
 legitimate non-whitelisted traffic from the private network is
 supposed to go to Internet, it’s not feasible to completely solve the
 issue.

App-1
-----

*Threat*:

 A malicious application reads another application’s private data. A
 malicious application wants to kill, debug or manipulate another
 application.

*Solution*:

 Applications run under different Unix IDs.

 Containers separate applications.

*Extensions*:

 Smack as MAC can prevent accidental sharing of data between
 applications (incorrect protection bits).

 Applications can share data with each other by belonging to a
 suitable sharing group (such as “media”). Users belonging to that
 groups can read and write to a directory in a shared
 area. Applications wishing to share more between each other must be
 started as the same user, which enables them to access each other’s
 data in the application data directory. If two applications want to
 share data and be containerized, they need to come from the same
 package (have a common manifest).

App-2
-----

*Threat*:

 A malicious or compromised application consumes all CPU, disk space
 or memory.

*Solution*:

 During root file system creation, reserve some disk space for root to
 use. If applications are run inside containers, set reasonable CPU
 and memory limits for the container using cgroups.

*Extensions*:

 Support quotas for user disk space limiting.

App-3
-----

*Threat*:

 A malicious or compromised application tries to access a sensor or
 actuator that it has no right to access.

*Solution*:

 For local sensors, use DAC groups for controlling access to files
 in ``/dev`` and ``sysfs``. Configure Udev to set proper owners, groups and
 permissions to the files controlling kernel access to local sensors,
 such as ``/sys/class/gpio``.

 For remote sensors, use Soletta to access the sensors. Open Connectivity Foundation (OCF)
 defines a
 security model which Soletta implements. The application can use
 Soletta features for secure provisioning of sensors. For more complex
 authentication needs, applications need to carry the burden by having
 authorization mechanism such as a certificate for accessing
 pre-configured sensors.

*Extensions*:

 More remote sensor security models can be implemented by adding support for them to Soletta.

API-1
-----

*Threat*:

 Unauthorized access to kernel APIs, for example for privilege escalation.

*Solution*:

 DAC for ``sysfs`` and ``/dev`` files.

*Extensions*:

 Use seccomp from manifest / systemd service files.


API-2
-----

*Threat*:

 Unauthorized access to middleware APIs to trigger actions (like
 system shutdown) or access information (status signals, queries).

*Solution*:

 Traditional DAC-based D-Bus access management. Disable unused (or
 unusable) system services.

*Extensions*:

 Patch upstream services depending on PolicyKit or shim that emulates
 PolicyKit (for example, based on Cynara).

API-3
-----

*Threat*:

 Application misrepresents another application towards cloud by
 stealing or guessing the information needed by the authorized
 application to identify itself.

*Solution*:

 Offer a secure storage mechanism that applications can use, for
 example gSSO or a TPM.

Threats and Attack Vectors Out of Scope for Ostro OS 1.0 Release
================================================================

* external DoS
* attack from compromised cloud (actuation, configuration, …)
* malicious activity in local network
* preventing access to the update server
* unauthorized upload of private data
* sensor DoS
* unauthorized access to sensor (on server/sensor side)
* attack using malicious data from a compromised sensor
* attacks that can affect the hardware, like causing a device
  to overheat
* attack vectors based on hardware that is specific to
  certain devices (like USB ports)
