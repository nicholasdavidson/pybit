.. _glossary:

Glossary of terms
#################

This glossary is not intended as an authoritative definition of terms
outside the scope of pybit itself. Some such terms (like :term:`chroot` and
:term:`debootstrap`) are included along with a reference to further
information on these tools. If there is a conflict between the tool
specific information and the glossary text, the tool specific information
should be used instead.

.. glossary::

  debianclient
    The pybit-client backend written to build Debian binary packages for
    the specified job.

  pybit client
    The ``pybit-client`` daemon which retrieves the job from the queue
    and passes the job to the selected backend then handles the results
    of the build to update the repository.

  build dependencies
    The name (and optionally the minimum version) of a package which
    **must** be fully installed before the build starts. Backends choose
    which programs are used to resolve these build dependency requirements
    and are usually heavily customised to the :term:`package format` in
    use.

  package format
    The package format is something like ``deb`` which denotes the format
    of the binary packages which the build is expected to create and
    handle.
     * deb == Debian, also compatible with Ubuntu and other Debian derivatives.

  debootstrap
    A Debian tool which can be used on multiple operating systems to
    create a minimal Debian system in a clean subdirectory suitable for
    use with :term:`chroot`. See ``man debootstrap`.

  chroot
    A chroot is a directory containing the set of files and directories
    sufficient to run a different (but compatible) operating system. The
    chroot can change between compatible architectures, virtualisation is
    not involved. e.g. a RedHat or Android system can have a Debian chroot.
    A 64bit x86 system can have a 32bit x86 system. Whilst it is possible
    to have an arm chroot on an x86 system, it is not possible to use the
    `chroot` command to execute the files in that directory without
    adding emulation or other layers.
    For pybit, a chroot is expected to allow execution of the files
    and the `chroot` command will require execution of the files to allow
    further commands to be run inside the directory as if it was a complete
    new system. Commands run inside a chroot cannot normally affect the
    system outside the chroot, exceptions include some kernel or libc
    instructions like hostname.
    See ``man chroot`` for more information.

  schroot
    A Debian chroot support tool which is part of the ``sbuild`` package
    to support building Debian packages in an environment which starts
    off clean and can be easily cleaned after the build. See ``man schroot``
    or ``man sbuild`` for more information.

