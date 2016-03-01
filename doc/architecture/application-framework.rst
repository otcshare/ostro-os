.. _application-framework:

Ostro |trade| Application Framework
###################################


Background
==========

The Ostro Application Framework is minimalistic and mostly built
around systemd services and containers.  Porting
over your existing code or applications to the Ostro OS should need
only minimal effort and no 
mandatory changes to your code. Ideally, you'll only need to provide 
a small piece of additional Ostro OS-specific "application manifest" metadata
for your application and you're done.


Framework
=========

The Application Framework has two actual components: an
installer and a systemd generator. The details of the installer are
still open, since it is undecided in which format 3rd-party
applications will be delivered. At least `Clear Linux\* bundles`_  
and `XDG-APPs`_ are being considered
as alternatives. In either case, the
installer will be a simple wrapper script with minimal additional
functionality around a utility that takes care of installing an
application (in the eventually chosen format).

The systemd generator component produces systemd service files for the
applications using information from the application manifest.

.. _Clear Linux\* bundles: https://clearlinux.org/documentation/index_bundles.html
.. _XDG-APPs: https://wiki.gnome.org/Projects/SandboxedApps



Usage of Containers
====================

Containers are used for filesystem 'virtualization' and for isolating
applications from each other. Applications can be packed together with
libraries they depend on. Application specific libraries are visible
only to the applications they are bundled with, not to the rest of the
system. While applications are installed in non-standard locations
``(/apps/*)``, the runtime view of the filesystem provided to an
application looks like a standard one (configuration files in
``/etc``, libraries in ``/usr/lib[64]``, binaries in ``/usr/[s]bin,
etc``), application-specific and system-wide bits blended together
using a combination of bind-mounts and overlay-mounts.


Container Types
================

The Ostro OS supports systemd-nspawned containers and (we're looking into
supporting) XDG-APPs inside containers. If configured so in the
manifest, applications can be started without containers by
augmenting ``$LD_LIBRARY_PATH``, ``$PATH``, and overriding ``$HOME``
appropriately.  We may also support adding 
new container types through simple plugins in the generator. The plugin
would receive the container-specific fragments of the manifests and
generate the necessary bits (mostly the ``ExecStart*`` parts) in the
systemd service as it sees fit. This is how the nspawn-specific code
already works in the Ostro OS, the only difference being that it is
not loaded as a Dynamic Shared Object (DSO), rather it is compiled statically into the
generator.


Manifests
=========

Sometimes it might be necessary or desirable to limit the
available functionality and configurability exposed to
applications. In other words, it might be necessary or desirable to
present a simplified manifest to the applications with less
configurability (and less possibility for errors). For instance, we may have a 
limited set of predefined application classes from
which an application provider must choose; one that best fits its
application. In this case, most of the configuration for the
application comes implicitly by selecting the application class,
instead of being explicitly stated in the manifest. The idea of having
such a possibility is good. However, we have not defined
how many and what such classes would be.

For now, we'll support both the "limited and simplified" and the "full"
configurability and let end-users choose which one they go with.
To enable this, we'll allow the user-visible manifest to be fed
to a 'preprocessor' (again a simple plugin/DSO) before it is passed on
to the core of the systemd service generator. The preprocessor can do
arbitrary translations (JSON-in-JSON-out) of the manifest. The Ostro OS contains
a sample preprocessor which can currently interpret the following
manifest format::

  /*
  * Application manifest keys:
  *
  *   - application: string
  *         Application identifier, mostly used for generating a few
  *         filesystem paths and file names.
  *
  *   - description: string
  *         A verbose description of the application.
  *
  *   - provider: string
  *         Unix user the application is executed as.
  *
  *   - groups: string
  *         If given, the Unix group the application is executed as.
  *
  *   - environment: dictionary (strings keys with string values)
  *         Extra environment variables to set for the application.
  *
  *   - command: array (of strings)
  *         The command line to start the application.
  *
  *   - autostart: boolean
  *         Whether to automatically attempt to start the application
  *         upon system boot.
  *
  *   - container: dictionary
  *         If the application is to be run inside a container, specifies
  *         the configuration for the container. Note that currently only
  *         systemd-nspawned containers are supported.
  *
  *         o type: string
  *             Container type to use, currently must be 'nspawn'.
  *         o network: string
  *             Container network configuration. Currently 'VirtualEthernet'.
  *         o sharedsystem: boolean
  *             Whether to run the container in a shared PID, UTS, and IPC
  *             namespaces.
  *
  */

  {
    "application": "sample-app",
    "description": "An application for frobnicating foobar and xyzzy.",
    "provider": "provider-1",
    "groups": "provider-1-group",
    "environment": {
        "FROB": "nicate",
        "FOOBAR": "xyzzy",
    },
    "command": [ "/usr/bin/test-1.sh" ],
    "autostart": "true",
     "container": {
        "type": "nspawn",
        "network": "VirtualEthernet",
        "sharedsystem": false,
    },
  }


Building an Application Using the Ostro Application Framework
==============================================================

The Ostro Application Framework includes a set of very simple sample
applications illustrating how to bind your application to the
framework. There's a "hello world" application in native C with
autotools and a similar server application in NodeJS.

Porting your application to the Ostro Application Framework requires only
a few simple steps:

1. Write the `Yocto Project recipe`_ for your application
2. Inherit from ostro-app class in your recipe
3. Define OSTRO_USER_NAME and OSTRO_APP_NAME in your recipe
4. Write a manifest for your application and include it to your recipe

.. _Yocto Project recipe: http://www.yoctoproject.org/docs/current/dev-manual/dev-manual.html#new-recipe-writing-a-new-recipe
.. _Yocto Project class: http://www.yoctoproject.org/docs/current/ref-manual/ref-manual.html#ref-classes
.. _useradd class: http://www.yoctoproject.org/docs/current/ref-manual/ref-manual.html#ref-classes-useradd

We have a simple helper `Yocto Project class`_ called "ostro-app" which you can
inherit to your application to make things a bit easier::
  
  inherit useradd

  # Tell useradd where the post-install script should go.
  USERADD_PACKAGES = "${PN}"
  
  # Set the defaults
  OSTRO_USER_SHELL ??= "/sbin/nologin"
  OSTRO_USER_APP_NAME ??= "${OSTRO_USER_NAME}-${OSTRO_APP_NAME}"
  
  # Create the user with disallowed login and no extra groups.
  USERADD_PARAM_${PN} = "-s ${OSTRO_USER_SHELL} ${OSTRO_USER_APP_NAME}"
  GROUPADD_PARAM_${PN} = ""
  GROUPMEMS_PARAM_${PN} = ""
  
  OSTRO_APP_DIR ??= "/apps"
  OSTRO_APP_ROOT ??= "${OSTRO_APP_DIR}/${OSTRO_USER_NAME}/${OSTRO_APP_NAME}"
  
  export OSTRO_APP_ROOT
  RDEPENDS_${PN} += "iot-app-fw"
  
  do_install_append () {
    chmod -R 755 ${D}${OSTRO_APP_ROOT}/
  }

Basically this class is inheriting from the Yocto Project oe-core `useradd class`_
which helps create users on the first boot of the device. User name
is a catenation from the OSTRO_USER_NAME and OSTRO_APP_NAME you give in
your application recipe. Also a home directory will be created for the
user. What this means in practice is that we have a dedicated user for
each app running in the system. The class will also create the
dedicated "apps" directory for the user/app combination and export
OSTRO_APP_ROOT variable for you to use in your recipe to install
applications to correct place.

Here is the simplified recipe for the sample "hello-world" C program::
  
  OSTRO_USER_NAME = "yoyodine"
  OSTRO_APP_NAME = "nativetest"
  
  SRC_URI = "file://hello-world.c"
  SRC_URI = "file://manifest"
  
  inherit ostro-app
  
  FILES_${PN} = "${OSTRO_APP_ROOT}/bin"
  FILES_${PN} =+ "${OSTRO_APP_ROOT}/manifest"
  
  PACKAGES = "${PN}"

And here is the manifest for the hello-world C program::
  
  {
    "application": "nativetest",
    "description": "test native application to see if the infra worked",
    "provider": "yoyodine",
    "groups": "yoyodine-nativetest",
    "environment": {
        "FROB": "nicate",
	"FOOBAR": "xyzzy",
    },
    "command": [ "/bin/hello-world" ],
    "autostart": "false",
    "container": {
        "type": "nspawn",
        "network": "VirtualEthernet",
        "sharedsystem": false,
    },
  }

When this application is added to the image, user
``yoyodine-nativetest`` is created in the first boot or when
installing the application. Also application framework systemd service
file generator is running at boot and generates a service file for
the application.  You should see the application under
``/apps/yoyodine/nativetest`` and you can see the user
``yoyodine-nativetest`` for example in ``/etc/passwd``. The generated
systemd service file should be in
``/run/systemd/generator/yoyodine-nativetest.service``.

You can now start and stop your application with ``systemctl`` (like
``systemctl start yoyodine-nativetest.service``). From the service
file you can see what happens: systemd-nspawn container is created
with the defined user, your application directory is overlay mounted, and
the applications is started in the container.
