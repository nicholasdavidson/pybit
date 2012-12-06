#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       buildclient.py
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
import pybit

class VersionControlHandler(object):
	def fetch_source(self):
		pass

	def get_srcdir (self):
		pass

	def clean_source (self, pkg) :
		pass

	# support test cases
	def is_dry_run (self):
		return self.settings["dry_run"]

	def __init__(self, settings):
		self.workdir = ""
		self.settings = settings
		if not "dry_run" in self.settings:
			self.settings["dry_run"] = True
		if not "buildroot" in self.settings:
			self.settings["buildroot"] = "/tmp/buildd"

class PackageHandler(object):

	chan = None
	logdir = None

	def __init__(self, settings):
		self.settings = settings
		if not "dry_run" in self.settings:
			self.settings["dry_run"] = True
		if not "buildroot" in self.settings:
			self.settings["buildroot"] = "/tmp/buildd"
		self.logdir = os.path.join(self.settings["buildroot"], "logs")
		if not os.path.isdir (self.logdir) and not self.settings["dry_run"] :
			os.mkdir (self.logdir)

	def get_buildlog (self, buildroot, buildreq) :
		logfile = None
		stamp = buildreq.get_buildstamp()
		if (stamp is not None) :
			log = "%s_%s-%s-%s" % (buildreq.get_package(), buildreq.get_version(), buildreq.get_arch(), buildreq.get_buildstamp())
			logfile = os.path.join (self.logdir, log)
		return logfile

	def is_dry_run (self):
		return self.settings["dry_run"]

	def build_master (self, buildroot):
		pass

	def build_slave (self, buildroot):
		pass

	def update_environment (self,name,pkg) :
		pass

	def upload (self, dirname, changes, pkg) :
		pass

	def get_distribution (self):
		pass
