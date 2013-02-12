#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       apt.py
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
from pybitclient.buildclient import VersionControlHandler

class AptClient(VersionControlHandler):
	def fetch_source(self, buildreq, conn_data):
		retval = None
		if buildreq.transport.method != "apt":
			retval = "wrong_method"
		if not retval :
			self.workdir = os.path.join (self.settings["buildroot"],
				buildreq.get_suite(), buildreq.transport.method, buildreq.get_package())
			if not os.path.isdir (self.workdir):
				pybitclient.mkdir_p (self.workdir)
			apt_path = os.path.join (self.workdir, "lists", "partial")
			pybitclient.mkdir_p (apt_path)
			apt_path = os.path.join (self.workdir, "archives", "partial")
			pybitclient.mkdir_p (apt_path)
			apt_path = os.path.join (self.workdir, "etc", "apt", "preferences.d")
			pybitclient.mkdir_p (apt_path)
			apt_path = os.path.join (self.workdir, "sources.list")
			src_list = os.open (apt_path, os.O_CREAT | os.O_WRONLY)
			url = "deb-src %s %s main" % (buildreq.transport.uri, buildreq.get_suite())
			os.write (src_list, url)
			cfg_str = "-o Apt::Get::AllowUnauthenticated=true -o Dir=%s -o Dir::State=%s -o Dir::Etc::SourceList=%s/sources.list -o Dir::Cache=%s" % \
				(self.workdir, self.workdir, self.workdir, self.workdir)
			command = "(cd %s && apt-get %s update 2>/dev/null || true)" % (self.workdir, cfg_str)
			if not retval :
				if pybitclient.run_cmd (command, self.settings["dry_run"], None) :
					retval = "update_apt"
			if (buildreq.get_version() is not None):
				command = "(cd %s/.. && apt-get %s -d source %s=%s )" % (self.workdir, cfg_str,
				buildreq.get_package(), buildreq.get_version() )
			else :
				command = "(cd %s && apt-get %s -d source %s )" % (self.workdir, cfg_str, buildreq.get_package() )
		if not retval :
			if pybitclient.run_cmd (command, self.settings["dry_run"], None) :
				retval = "fetch_source"
		if not retval :
			retval = "success"
		pybitclient.send_message (conn_data, retval)
		if retval == "success":
			return 0
		else :
			return 1

	def get_srcdir (self):
		return self.workdir

	def clean_source (self, buildreq, conn_data) :
		retval = None
		if buildreq.transport.method != "apt":
			retval = "wrong_method"
		if not retval :
			src_dir = os.path.join (self.settings["buildroot"], buildreq.get_suite(), buildreq.transport.method)
			src_changes = "%s/%s_%s.dsc" % (src_dir, buildreq.get_package(), buildreq.get_version() )
			command = "dcmd rm %s" % (src_changes)
			if pybitclient.run_cmd (command, self.settings["dry_run"], None):
				retval = "source-clean-fail"
		if not retval :
			self.cleandir = os.path.join (self.settings["buildroot"], buildreq.get_suite(), buildreq.transport.method,
				buildreq.get_package())
			command = "rm -rf %s/" % (self.cleandir)
			if pybitclient.run_cmd (command, self.settings["dry_run"], None) :
				retval = "failed_clean"
		if not retval :
			retval = "success"
		pybitclient.send_message (conn_data, retval)
		if retval == "success":
			return 0
		else :
			return 1

	def __init__(self, settings):
		VersionControlHandler.__init__(self, settings)
		self.method = "apt"

def createPlugin (settings) :
	return AptClient (settings)
