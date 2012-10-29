#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       subversion.py
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
from buildclient import PackageHandler, VersionControlHandler

class SubversionClient(VersionControlHandler):
	def fetch_source(self, pkg, conn_data):
		retval = None
		if pkg.method_type != "svn":
			retval = "wrong_method"
		if not retval :
			self.workdir = os.path.join (self.options["buildroot"], pkg.suite, pkg.method_type)
			if (hasattr(pkg, 'vcs_id')):
				command = "svn export %s@%s %s" % (pkg.uri, pkg.vcs_id, self.workdir)
			elif (hasattr(pkg, 'uri')):
				command = "svn export %s %s" % (pkg.uri, self.workdir)
			else:
				print "Could not fetch source, no method URI found"
				retval = "unrecognised uri"
		if not retval :
			if not pybitclient.run_cmd (command, self.option["dry_run"]) :
				retval = "fetch_source"
		if not retval :
			retval = "success"
		pybitclient.send_message (conn_data, retval)

	def get_srcdir (self):
		return self.workdir

	def clean_source (self, pkg) :
		retval = "success"
		if pkg.method_type != "svn":
			retval = "wrong_method"
		if not retval :
			self.cleandir = os.path.join (self.options["buildroot"], pkg.suite)
			command = "rm -rf %s/*" % (self.cleandir)
			if not pybitclient.run_cmd (command, self.option["dry_run"]) :
				retval = "failed_clean"
		pybitclient.send_message (conn_data, retval)

	def __init__(self):
		VersionControlHandler.__init__(self)
