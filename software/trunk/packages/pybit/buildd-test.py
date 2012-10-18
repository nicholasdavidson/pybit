#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       buildd-test.py
#
#       Copyright 2012 Neil Williams <codehelp@debian.org>
#
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

import os
import pybitclient
from pybitclient.subversion import SubversionClient
from pybitclient.debian import DebianBuildClient

def main():
	conffile = "%s/pybitclient/client.conf" % (os.getcwd());
	if os.path.isfile (conffile):
		options = pybitclient.get_settings(conffile)
	else :
		options = pybitclient.get_settings("/etc/pybit/client/client.conf")
	pkg = pybitclient.deb_package ("")
	pkg.vcs_id = "21094"
	pkg.method_type = "svn"
	pkg.suite = "pybit"
	pkg.package = "pybit"
	pkg.version = "0.0.25"
	pkg.architecture = "i386"
	pkg.source = "pybit"
	pkg.uri = "http://svn/svn/lwdev/software/trunk/packages/pybit"
	vcs = SubversionClient ()
	vcs.fetch_source (pkg)
	srcdir = vcs.get_srcdir()
	client = DebianBuildClient ()
	# To check the build-dependencies in advance, we need to ensure the
	# chroot has an update apt-cache, so can't use apt-update option of
	# sbuild. The alternative is to update the apt-cache twice per build,
	# once for the dep check and once before the build. The choice depends
	# on whether two network trips are more efficient than rewriting the
	# lvm snapshot before even trying to do any build.
	if options["use_lvm"] :
		name = pkg.suite + "-source"
	else:
		name = pkg.suite
	client.update_environment (name, pkg)
	while client.is_building() :
		wait(self)
	pkg.buildd = options["idstring"]
	pkg.msgtype = "building"
	client.build_master (srcdir, pkg)
	pkg.vcs_id = ""
	pkg.package = "textparser"
	pkg.version = "0.0.13"
	pkg.architecture = "i386"
	pkg.source = "textparser"
	pkg.uri = "http://svn/svn/lwdev/software/trunk/packages/textparser"
	vcs.fetch_source (pkg)
	client.build_slave (srcdir, pkg)

	return 0

if __name__ == '__main__':
	main()

