.. _glossary:

Glossary of terms
#################

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
