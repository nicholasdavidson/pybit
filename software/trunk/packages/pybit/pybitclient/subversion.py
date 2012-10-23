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

report_name = "controller"

class SubversionClient(VersionControlHandler):
	def fetch_source(self, pkg):
		try:
			if pkg.method_type != "svn":
				return
			self.workdir = os.path.join (self.options["buildroot"], pkg.suite, pkg.method_type)
			pybitclient.mkdir_p (self.workdir)
			if os.path.isdir(self.workdir) :
				os.chdir (self.workdir)
			else:
				return
			if (hasattr(pkg, 'vcs_id')):
				command = "svn export %s@%s" % (pkg.uri, pkg.vcs_id)
			elif (hasattr(pkg, 'uri')):
				command = "svn export %s" % (pkg.uri)
			else:
				print "Could not fetch source, no method URI found"
				return
			if not self.run_cmd (command, "failed", pkg, report_name, self.options["dry_run"]):
				return
			return
		except Exception as e:
			raise Exception('Error fetching source: ' + str(e))
			return

	def get_srcdir (self):
		return self.workdir

	def clean_source (self, pkg) :
		if pkg.method_type != "svn":
			return
		self.cleandir = os.path.join (self.options["buildroot"], pkg.suite)
		if os.path.isdir(self.cleandir) :
			os.chdir (self.cleandir)
			command = "rm -rf ./*"
			if not self.run_cmd (command, "failed", pkg, report_name, self.options["dry_run"]) :
				return
			return

	def __init__(self):
		VersionControlHandler.__init__(self)
