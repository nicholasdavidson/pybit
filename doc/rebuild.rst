Rebuilding Debian packages using apt
************************************

Automatic rebuilds of packages in Debian
========================================

Debian posts all package changes to the debian-devel-changes mailing
list: https://lists.debian.org/debian-devel-changes/

A particular email address can then be subscribed to this list and forward
the emails (which all contain a .changes file for the package concerned)
to the changes-debian hook. This will send a message to the controller at
the specified location with enough information to rebuild the specified
package in the relevant suite and upload it.

For example, this can be used to automatically rebuild Debian packages
as soon as the package arrives in the archive. Note that there will be a
delay before the package itself becomes available on your current mirror,
so your list of "waiting" packages will get quite long.

The changes-debian hook operates via STDIN. The expected interface is
that procmail forwards each email to the hook. The hook is written in
perl and can be extended to not send a curl message for particular
suites, package names or other filters.

local rebuilds
==============

An alternative use of the same support is to pass a .changes file at
the changes-debian hook whenever a local package is built - this allows
PyBit to build the package ahead of the commit.

The changes-debian hook also allows for rebuilds of packages not
currently in a VCS configured to use PyBit upon commit.

Note: this could allow developers to put packages into repositories
before the package is ready, so it is as well to be aware of this and
decide whether the changes hook will be available.

If local changes have a different suite to production builds, this
could itself be useful - it depends how PyBit is setup / used.
