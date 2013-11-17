.. rst syntax described at http://sphinx-doc.org/rest.html

Pybit Manual
############

What is pybit?
**************

Pybit is a queue with hooks at one end and a build system at the other.

A pybit system consists of devices with a set of roles:
* a controller to host the database and web frontend
* at least one client with build chroots
* a repository to which packages can be uploaded

Pybit has modular support for backends and hooks. Current backends rely
on Debian support (like ``sbuild`` and ``dpkg``) and the default
:term:`watcher` has support only for ``reprepro`` but other processes can be
used as a watcher.

Why use pybit?
**************

To reliably build collections of binary packages directly from source
code in a variety of build environments, on a variety of architectures
and upload to a variety of suites.

Currently, pybit is focused on Debian packaging but other backends can
be written for the :term:`pybit client`. Builds start when a hook adds a job to
the queue. Hooks can be any script which provides relevant information
to the queue, including which backend to use. pybit retains the order
from the queue, so if the hook is intelligent, pybit doesn't try to
second-guess the ordering. If the backend is capable of detecting
failures entirely due to missing :term:`build dependencies`, pybit can
re-queue that build to try again later.

* Build in clean chroots.
* Distributed across a pool of available build clients.
* Automated End-To-End solution.
* Extensible package format support and VCS backends.
* Uses common debian tools under the hood.
* Minimal dependencies at the client end.

Setting up pybit
****************

The recommended way to setup and run pybit is to install or build
the Debian packages.

Pybit does not support running on Debian Squeeze, Ubuntu Precise 12.04LTS
or older but it can build packages for squeeze or precise and older.

Wheezy is supported and packages exist in Jessie. In Ubuntu, pybit
is included in Saucy Salamander (13.10).

http://packages.qa.debian.org/p/pybit.html

Installation from git
=====================

To prepare local test builds directly from git (without using an
existing tag or creating a new tag), use the setuptools.py to create a
tarball::

 $ python setup.py sdist

The Debian packaging is separate: https://github.com/codehelp/pybit-debian
and packages are available in Debian and Ubuntu.
http://packages.qa.debian.org/p/pybit.html

To build a debian package from a sdist tarball you need to look at the
``debian/README.source`` and also use a .gbp.conf like the following::

 [DEFAULT]
 builder = debuild
 cleaner = fakeroot debian/rules clean
 pristine-tar = True

 [git-buildpackage]
 export-dir = ../build-area/
 tarball-dir = ../tarballs/

 [git-import-orig]
 dch = False

Installation on Debian
======================

Current packages use debconf to ask about specific strings and set some
Debian-based defaults.

debconf asks the user for details of:

* The clientid string for this client (must not be empty and needs to
  be unique for each client using any one RabbitMQ server).
* The location of the rabbitMQ server to receive build messages (can
  be omitted if not configured at this point but needs to be specified
  in ``/etc/pybit/client/client.conf`` and the client restarted or no
  builds will be started).
* The codename of the location to upload the built packages (must not
  be empty as the default for ``dput`` is typically to upload to
  ``ftp-master.debian.org``).

The maintainer scripts calculate default values for:

* The native architecture of this client, e.g. i386::

   $ dpkg-architecture -qDEB_BUILD_ARCH)
* The distribution in use, e.g. Debian::

   $ dpkg-vendor --query vendor

debconf also has some low priority questions::
 * Whether lvm snapshots are in use (default is true).
 * Whether to change the default buildd location of ``/home/buildd/pybit``

These options are accessible using::

 # dpkg-reconfigure pybit-client

Post install setup
******************

Debian setup
============

A lot of the post installation setup is based on Debian tools and Debian
methods. If someone writes backends which use other formats, the
documentation can be updated with the backend-specific steps required for
the :term:`package format` added with that backend.

Finally, there are also configuration settings in ``/etc/pybit/client/client.conf``
which provide more options. (Changes to this file will update the
corresponding debconf values when ``dpkg-reconfigure pybit-client`` is run.)

::

 {
  "pkg_format": "deb",
  "port": "5672",
  "userid": "guest",
  "password": "guest",
  "vhost": "/",
  "dput": "-U",
  "debconf": true
 }

The configuration file is in JSON format and debconf adds the last line
via the maintainer script.

  pkg_format
    used by each build client to screen out unsupported binary formats,
    e.g. Debian clients will check for deb and RPM clients would
    check for rpm. See :ref:`package_formats`

  port
   If your RabbitMQ server is configured to use a non-standard port,
   specify that here.

  userid
   If the RabbitMQ server uses authentication, specify the username here.

  password
   If the RabbitMQ server uses authentication, specify the password here.

  vhost
   If the RabbitMQ server uses a specific VHost, specify that here.

  dput
   options passed down to dput - see ``man 1 dput``. The default is to
   stop dput writing .upload files.

Adding Debian build chroots
---------------------------

The detailed process of creating a :term:`chroot` suitable for :term:`schroot` is covered
in the :term:`sbuild` documentation (man 5 schroot.conf) and amounts to using a
tool like :term:`debootstrap` to create a Debian build environment in a
subdirectory (which may or may not be also the mountpoint of an LVM
snapshot) and then configuring that chroot to have the relevant apt
sources and pre-installed packages (e.g. ``build-essential`` and ``dpkg-dev``).

.. note:: when creating a chroot for schroot, remember to use the
   ``--variant=buildd`` option to debootstrap and install fakeroot inside
   the chroot.

::

 sudo debootstrap --variant=buildd stable /srv/chroots/stable http://ftp.uk.debian.org/debian
 sudo sbuild-createchroot unstable /srv/chroot/unstable http://ftp.uk.debian.org/debian

.. note:: If you are trying to set up a Debian chroot on Ubuntu, and
    this is not working, please see issue #138
    https://github.com/nicholasdavidson/pybit/issues/138

If this is the first time you've setup sbuild, generate a key::

 sbuild-update --keygen

Accessing the chroot
--------------------

If not using LVM::

 sudo schroot -u root -c unstable

If not using LVM::

 sudo schroot -u root -c unstable-source

chroots not using LVM will not check build-dependencies separately from
the package build.

If a build client cannot use LVM, the pre-build dependency check will be
turned off as there is a risk that it may leave build-dependencies
installed when using permanent chroots. (See https://github.com/nicholasdavidson/pybit/issues/61).
This will mean that pybit may report a package as failing to build on such
clients when what actually happened is that the package build-dependencies
could not be resolved.

lvm chroots may need extra setup
--------------------------------

Initial debootstrap setup can provide files which then cause problems the
first time that a core package is installed. So, as LVM is a fresh install
each time, it is best to fix these problems in the LVM source before trying
to do builds. Example packages: netbase (/etc/protocols). This is particularly
likely when using debootstrap from stable to setup LVM chroots for unstable -
debootstrap copies certain files from the host system into the new chroot but
these files then differ from the ones packaged in unstable.

Install pbuilder
----------------

The pybit :term:`debianclient` uses ``/usr/lib/pbuilder/pbuilder-satisfydepends-classic``
for the dependency resolution test, so the ``pbuilder`` package needs to
be installed inside each build chroot::

 sudo schroot -u root -c unstable
 apt-get --no-install-recommends install pbuilder

Permission checks

Everything in and beneath the pybit buildd directory (e.g.
``/home/buildd/pybit``) needs to be owned by the buildd user used by
sbuild.

Naming the chroots
------------------

The pybit client will expect to be able to use a chroot (or an alias for
a chroot) which matches the suite specified in the build request. If
using version control hooks, this suite is likely to come from the
Distribution field of the output of ``dpkg-parsechangelog``. Ensure that any
client has a suitable chroot listed in the output of ``schroot -l``.

pybit-client only listens to queues which match the listed suites in
``/etc/pybit/client/client.conf``.

The syntax for the suites configuration value changed in version 0.4.1
to support multiple suites within a JSON list:

::

  "suites": [ "unstable", "squeeze-backports" ],

Clients running 0.4.0 need to have the configuration file updated for
0.4.1 or the client will fail to start as it will be unable to bind to
the necessary queues.

If using version control hooks, this suite is likely to come from the
Distribution field of the output of ``dpkg-parsechangelog``. Ensure
that any client has a suitable chroot listed in the output of ``schroot -l``.
The suite should specified in ``/etc/pybit/client/client.conf`` as this
will determine which queues the client will use to receive build
requests. Multiple suites are supported by appending multiple suites
to suites key in ``client.conf``.

For example::

 { "suites": ["testing","stable","oldstable"] }

Testing the chroots
===================

There is a test script (``/usr/share/pybitclient/buildd-test.py``) which can
be used alongside a test schroot to run through the buildd commands and
then do the upload. (What happens to that upload is dependent on the
next step, it just sits in an incoming directory initially.)

Configuring the upload handler
==============================

Set up dput by editing ``/etc/pybit/client/dput.cf`` to provide a usable
upload configuration. The format of this file is the same as ``~/.dput.cf``
and is passed to dput using the -c option internally. See dput.cf (5)

Configuring the upload handler, dput

Set up dput by editing /etc/pybit/client/dput.cf to provide a usable
upload configuration. The format of this file is the same as ``~/.dput.cf``
and is passed to dput using the -c option internally.

Ensure the daemon can upload::

 sudo ssh -o IdentityFile=/home/<USER>/.ssh/id_rsa <USER>@<DESTINATION>

Where is something like buildd and something like mirror.domain

Enabling the builds
===================

Pybit clients are configured in dry_run mode initially. The final stage
of setting up a particular client is then to edit ``/etc/pybit/client/client.conf``
to change dry_run to false::

 "dry_run": false,

Setting up a pybit client
=========================

If your package installation has not created ``/etc/pybit/client/client.conf``,
stop the client, copy it from ``/usr/share/pybitclient/client.conf`` and
restart the client after editing.

Configure pybit-client itself

Edit /etc/pybit/client/client.conf for this specific buildd client.

* Specify the idstring for this client
* Specify the native architecture of this client. (cross-build support is pending #4)
* Specify if lvm is in use (default is true)
* Specify if the client should run in simulation mode which prints the
  commands it would run instead of executing the commands.
* Specify a user-writable location for the VCS to write the source, for
  the .dsc to be generated and for the buildlogs to be written.
* Specify the location of the RabbitMQ server. (not needed for the initial tests)
* Specify any dput options, e.g. -U to not generate .upload files.
* The location of the machine providing the webAPI and controller
  queues is specified within each build request message and is not
  configured by the client, only the location of the RabbitMQ server
  itself.

Tools to be configured per setup:

repository management, e.g. reprepro.
pybit-web

Adding a suite
--------------

Adding an architecture
----------------------

Adding a build environment
--------------------------

Advanced Build Environments and Suite Arch Combinations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On the Software Suites page, enter the name of a software suite to add
it to the database. Examples of suites include 'development' or
'chickpea'. One example of when you would need to add something to this
list, is if you make a new release branch.

On the Architectures page, enter the name of a package architecture to
add it to the database. Examples of such architectures include 'i386'.
One example of when you would need to add something to this list, is if
a new platform becomes supported.

Also on this page, you can define Suite/Architectures relationships,
allowing you to manage the supported build architecture combinations
for each suite. For example, you could add mappings for a 'stable' suite
to both 'i386' and 'ARM' architectures, but only add a single mapping for
the 'i386' architecture on the 'development' suite. You can also add a
'master_weight' value to each mapping. The mapping with highest
'master_weight' value will determine the 'master' build for that
particular 'suite'.

On the Build Environments page, enter the name of a build environment
to add it to the database. Examples of such environments include
'squeeze' and 'wheezy'.

Also on this page, you can define Build Environment / Suite Arch
relationships, allowing you to manage the supported build environment
and architecture combinations for each suite. For example, you could
create mappings for the 'development/i386' suite arch (see above) and
both 'squeeze' and 'wheezy', this would allow you to build the packages
for the same suite on multiple build environments. If you do not
specify a build environment, it will simply build by suite, depending
on your schroot/sbuild config.

Packages built using the build environment will be uploaded for a suite
named environment-suite name, e.g. building external on squeeze will
result in uploads targeted at squeeze-external.

The watcher configuration will also need to be updated to add the
second target.

Submitting your first job
*************************

Using an existing hook
======================

SVN Hook Setup
--------------

The SVN hook from ``pybit-svn`` does not depend on the rest of Pybit
or on Python. It provides a Subversion post commit hook to check for
interesting changes in the repository, being invoked after a commit has
completed.

Subversion invokes your ``post-commit`` script, passing in the path to
the repository, and the SVN Revision of the commit in question. Our hook
parses the debian changelogs etc... and uses "curl" to securely send
a message over HTTP to the pybit-web application, running on another
server.

To use, just put the hook in /[path to your repo]/hooks, and in the
``Configuration`` section, set "PYBIT_HTTP" field::

 http://[The FQDN of your pybit-web server]/job/vcshook

Then set "ANON_SVN" to the URI for anonymous read access to your SVN repo.

Using a direct call to curl
===========================

Creating a package instance to submit a job
*******************************************
