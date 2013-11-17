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

