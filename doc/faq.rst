.. _blacklisting:

Blacklisting packages
=====================

Sometimes there will be packages being committed to the VCS with
updated ``debian/changelog`` files but which either cannot or should
not be built automatically.

``pybit-web`` supports a postgres table called ``Blacklist``, with fields
``field`` and ``regex``. Blacklist is used internally by ``process_job()``
in controller to determine if certain packages are centrally blacklisted
using regexes. If there is a match on the field in question, ``pybit-web``
will not issue a build request for this package. ``process_job()`` is
called by both the WebGUI and the VCS hook.

For example ``name`` and ``(.*-dev)`` will mean we do not autobuild any
development packages, while ``vcs_uri`` and ``(.*/users/*)`` will
block sources from locations such as ``/repo/users/jamesb/somebadcode``

The controller log will print ``BLACKLISTED! - [regex] matches [fieldname]:[data]``
if a package is blacklisted.

A 403 will be returned, as well as a False, from process_job to its
caller (previously it returned void).

.. _resetting_rabbit:

Resetting rabbit
================

To wipe RabbitMQ state:

sudo rabbitmqctl reset or sudo rabbitmqctl force_reset

Note, you cant do this while it is running. DO NOT do something like
``sudo invoke-rc.d rabbitmq-server stop`` - Rather, do::

 sudo rabbitmqctl stop_app
 sudo rabbitmqctl reset
 sudo rabbitmqctl start_app

or::

 sudo rabbitmqctl stop_app
 sudo rabbitmqctl force_reset
 sudo rabbitmqctl start_app

You can confirm it worked by doing something like::

 sudo rabbitmqctl -n rabbit@tclpc02 list_queues

.. _package_formats:

Package formats
===============

  deb
    Debian, also compatible with Ubuntu and other Debian derivatives.

.. _build_environments:

Using build environments
------------------------

The pybit build client can also handle a build-environment parameter
which forms part of the name of the chroot. The typical use for this is
to build packages on top of a defined build suite. e.g. for an internal
suite which uses a Debian release to provide the core packages like
``dpkg-dev``, ``gcc`` and ``debhelper``. This allows jobs to be
requested for the same source code from a non-Debian release against
two different Debian releases to be used when the source code needs
to be checked against an upcoming release or in preparation for a
migration to a new Debian release. Such schroots would already have
two apt sources - one for Debian (either a local snapshot or a full
mirror) for the compiler and build tools and another for the non-Debian
dependencies such as the custom user interface or other code which is
expected to run on an installed Debian base. The client then needs to
have one chroot for each supported combination. For a non-Debian release
called foobar which contains code needing to be built in a Debian Wheezy
and a Debian Sid environment, this would require two chroots, called
foobar-wheezy and foobar-sid with the apt sources to match. Equally,
the target repository now needs a foobar-wheezy suite and a foobar-sid
suite so that devices can be switched from one suite to another to test
migration paths.

For example::

 { "suites": ["development-wheezy","development-sid","archive-squeeze"] }

It is an error to specify a build environment without a suite.

If a build request specifies a suite but not a build environment, the
build-environment is not used and the schroot aliases will need to
determine the default build environment.

amd64 building i386
^^^^^^^^^^^^^^^^^^^

amd64 machines can trivially build i386 packages using a simple chroot
and pybit-client can support this simply by editing the host_arch in
the ``/etc/pybit/client/client.conf`` file.

.. _bind_mounts:

Bind mounts
-----------

Most sbuild chroots have some form of bind mounting of useful directories
into the relevant chroots, created by editing ``/etc/fstab`` outside the
chroots. Certain tasks may fail if the pybit buildroot directory is not
visible inside the chroots; other packages may need a usable ``/dev``
and or ``/proc``. For example::

 $ schroot -c wheezy
 user@buildd:~$ mount
 warning: can't open /etc/mtab: No such file or directory

This output indicates that nothing is mounted inside the chroot - some
packages may fail to build and some pybit operations (like checking the
build-dependencies are available) may fail. If the pybit build directory
is in the /home/ tree, it is only necessary to bind mount the pybit
build directory, not the entirety of /home/.

