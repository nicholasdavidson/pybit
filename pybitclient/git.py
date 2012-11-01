#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       git.py
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
from buildclient import VersionControlHandler

class GitClient(VersionControlHandler):
	def fetch_source(self, buildreq, conn_data):
		retval = None
		#try:
		if buildreq.transport.method != "git":
			retval = "wrong_method"
		if not retval :
			self.workdir = os.path.join (self.options["buildroot"],
				buildreq.get_suite(), buildreq.transport.method)
			if (buildreq.transport.vcs_id is not None):
				# this needs multiple commands
				# git clone
				# git checkout <rev>
				command = "git clone %s@%s %s" % (buildreq.transport.uri,
					buildreq.transport.vcs_id, self.workdir)
			elif (buildreq.transport.uri is not None):
				command = "git clone %s %s" % (buildreq.transport.uri, self.workdir)
			else:
				print "Could not fetch source, no method URI found"
				retval = "unrecognised uri"
		if not retval :
			if not pybitclient.run_cmd (command, self.options["dry_run"]) :
				retval = "fetch_source"
		#except Exception as e:
		#	retval = str(e)
		if not retval :
			retval = "success"
		pybitclient.send_message (conn_data, retval)

	def get_srcdir (self):
		return self.workdir

	def clean_source (self, buildreq, conn_data) :
		retval = None
		if buildreq.transport.method != "git":
			retval = "wrong_method"
		if not retval :
			self.cleandir = os.path.join (self.options["buildroot"], buildreq.get_suite())
			command = "rm -rf %s/*" % (self.cleandir)
			if not pybitclient.run_cmd (command, self.options["dry_run"]) :
				retval = "failed_clean"
		retval = "success"
		pybitclient.send_message (conn_data, retval)

	def __init__(self):
		VersionControlHandler.__init__(self)
