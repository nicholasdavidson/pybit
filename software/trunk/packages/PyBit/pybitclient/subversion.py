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
from buildclient import BuildClient

class SubversionClient(BuildClient):

	workdir = ""
	options = {}

	def fetch_source(self):
		if pkg.method_type != "svn":
			return
		self.workdir = os.path.join (buildroot, pkg.suite, "svn")
		mkdir_p (workdir)
		if os.path.isdir(workdir) :
			os.chdir (workdir)
		else:
			return
		if (pkg.vcs_id):
			command = "svn export %s@%s" % (pkg.method_uri, pkg.vcs_id)
		else:
			command = "svn export %s" % (pkg.method_uri)
		if run_cmd (command, "failed", report_name, self.options["dry_run"]):
			return
		return

	def get_srcdir (self):
		return self.workdir

	def __init__(self):
		if os.path.isfile ("client.conf"):
			self.options =  pybitclient.get_settings("client.conf")
		elif os.path.isfile ("/etc/pybit/client/client.conf") :
			options = pybitclient.get_settings("/etc/pybit/client/client.conf")
		if len(self.options) > 0 :
			buildroot = self.options["buildroot"]
		else :
			self.options["dry_run"] = True
