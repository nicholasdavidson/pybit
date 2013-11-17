.. rst syntax described at http://sphinx-doc.org/rest.html

Pybit Manual
############

What is pybit?
**************

Pybit is a queue with hooks at one end and a build system at the other.

Why use pybit?
**************

To build binary packages from source code. 

Currently, pybit is focused on Debian packaging but other backends can
be written for the pybit client. Builds start when a hook adds a job to
the queue. Hooks can be any script which provides relevant information
to the queue, including which backend to use. pybit retains the order
from the queue, so if the hook is intelligent, pybit doesn't try to
second-guess the ordering. If the backend is capable of detecting
failures entirely due to missing build dependencies, pybit can re-queue
that build to try again later.

Setting up pybit
****************

Installation on Debian
=====================

Installation from git
=====================

Post install setup
==================

Adding build chroots
--------------------

The detailed process of creating chroots suitable for schroot is covered
in the sbuild documentation (schroot.conf (5)) and amounts to using a
tool like debootstrap to create a Debian build environment in a
subdirectory (which may or may not be also the mountpoint of an LVM
snapshot) and then configuring that chroot to have the relevant apt
sources and pre-installed packages (e.g. ``build-essential`` and ``dpkg-dev``).

.. note:: when creating a chroot for schroot, remember to use the 
   ``--variant=buildd`` option to debootstrap and install fakeroot inside
   the chroot.

Install pbuilder
^^^^^^^^^^^^^^^^

The pybit :term:`debianclient` uses ``/usr/lib/pbuilder/pbuilder-satisfydepends-classic``
for the dependency resolution test, so the ``pbuilder`` package needs to
be installed inside each build chroot.

Adding a suite
--------------

Adding an architecture
----------------------

Adding a build environment
--------------------------

Submitting your first job
=========================

Using an existing hook
----------------------

Using a direct call to curl
---------------------------

Creating a package instance to submit a job
--------------------------------------------

