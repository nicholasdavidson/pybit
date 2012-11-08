#!/bin/sh

#       Copyright 2012 Neil Williams <codehelp@debian.org>
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

set -e

DIR=$1
TGT=$2
/usr/lib/pbuilder/pbuilder-satisfydepends-classic --control ${1}/debian/control
# non-native packages commonly need a customised command to prepare the
# released tarball (which is what dpkg-buildpackage needs) from the
# VCS export/clone (from which the tarball was originally built).
# Building the tarball from VCS commonly requires the build-dependencies
# of the package to be installed, so this needs to happen inside the chroot.
# If the custom command is not available in debian/rules, clone the
# debian/ directory to a new repo and add it, then add any extra build-deps
# to debian/control and point the build at the new repo. Add or fix the
# debian/watch file if necessary.
(cd $1 ; fakeroot debian/rules $2 )
(cd $1 ; fakeroot dpkg-buildpackage -nc -S -d -uc -us)
