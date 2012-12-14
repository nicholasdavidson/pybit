#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       crossdebian.py
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
import logging
import pybitclient
from pybitclient.buildclient import PackageHandler
from pybit.models import BuildRequest, checkValue

class DebianCrossClient(PackageHandler):
	dput_cfg = ""
	dput_dest = ""

	def update_environment(self,name,pkg, conn_data):
		retval = "success"
		command = "schroot -u root -c %s -- apt-get update > /dev/null 2>&1" % (name)
		if pybitclient.run_cmd (command, self.settings["dry_run"], None) :
			retval = "build_update"
		pybitclient.send_message (conn_data, retval)
		if retval == "success":
			return 0
		else :
			return 1

	def build_master (self, buildreq, conn_data):
		retval = None
		logfile = self.get_buildlog (self.settings["buildroot"], buildreq)
		if (not isinstance(buildreq, BuildRequest)):
			logging.debug ("E: not able to identify package name.")
			retval = "misconfigured"
			pybitclient.send_message (conn_data, retval)
			return
		srcdir = os.path.join (self.settings["buildroot"],
				buildreq.get_suite(), buildreq.transport.method)
		package_dir = "%s/%s" % (srcdir, buildreq.get_package())
		command = "(cd %s ; dpkg-buildpackage -S -d -uc -us)" % (package_dir)
		if pybitclient.run_cmd (command, self.options["dry_run"], logfile):
			retval = "build-dep-wait"
		if not retval :
			command = "sbuild -n --debbuildopt=\"-a%s\" --setup-hook=\"/usr/bin/sbuild-cross.sh\" --arch=%s -A -s -d %s %s/%s_%s.dsc" % (
				pkg.architecture, pkg.architecture, pkg.suite, srcdir, pkg.source, pkg.version)
			if pybitclient.run_cmd (command, self.settings["dry_run"], logfile):
				retval = "build_binary"
		if not retval :
			changes = "%s/%s_%s_%s.changes" % (self.settings["buildroot"], buildreq.get_package(),
				buildreq.get_version(), buildreq.get_arch())
			if not self.settings["dry_run"] and not os.path.isfile (changes) :
				logging.debug("build_master: Failed to find %s file." % (changes))
				retval = "build_changes"
		if not retval :
			retval = "success"
		pybitclient.send_message (conn_data, retval)
		if retval == "success":
			return 0
		else :
			return 1

	def upload (self, buildreq, conn_data):
		retval = None
		logfile = self.get_buildlog (self.settings["buildroot"], buildreq)
		changes = "%s/%s_%s_%s.changes" % (self.settings["buildroot"], buildreq.get_package(),
			buildreq.get_version(), buildreq.get_arch())
		if not os.path.isfile (changes) and not self.settings["dry_run"]:
			logging.debug("upload: Failed to find %s file." % (changes))
			retval = "upload_changes"
		if not retval :
			command = "dput -c %s %s %s %s" % (self.dput_cfg,
				self.settings["dput"], self.settings["dput_dest"], changes)
			if pybitclient.run_cmd (command, self.settings["dry_run"], logfile):
				retval = "upload_fail"
		if not retval :
			command = "dcmd rm %s" % (changes)
			if pybitclient.run_cmd (command, self.settings["dry_run"], logfile):
				retval = "post-upload-clean-fail"
		if not retval :
			retval = "success"
		pybitclient.send_message (conn_data, retval)
		if retval == "success":
			return 0
		else :
			return 1

	def build_slave (self, buildreq, conn_data):
		retval = None
		logfile = self.get_buildlog (self.settings["buildroot"], buildreq)
		srcdir = os.path.join (self.settings["buildroot"],
				buildreq.get_suite(), buildreq.transport.method)
		package_dir = "%s/%s" % (srcdir, buildreq.get_package())
		if os.path.isdir(package_dir) or self.settings["dry_run"]:
			command = "(cd %s ; dpkg-buildpackage -S -d -uc -us)" % package_dir
			if pybitclient.run_cmd (command, self.settings["dry_run"], logfile):
				retval = "build_dsc"
			if not retval :
				command = "sbuild -n --apt-update -d %s %s/%s_%s.dsc" % (
					buildreq.get_suite(), srcdir,
					buildreq.get_package(), buildreq.get_version())
				if pybitclient.run_cmd (command, self.settings["dry_run"], logfile):
					retval = "build_binary"
			if not retval :
				changes = "%s/%s_%s_%s.changes" % (self.settings["buildroot"],
					buildreq.get_package(), buildreq.get_version(),
					buildreq.get_arch())
				if not self.settings["dry_run"] and not os.path.isfile (changes) :
					logging.debug ("build_slave: Failed to find %s file." % (changes))
					retval = "build_changes"
		else:
			retval = "Can't find build dir."
		if not retval :
			retval = "success"
		pybitclient.send_message (conn_data, retval)
		if retval == "success":
			return 0
		else :
			return 1

	def get_distribution (self) :
		return 'Debian-Cross'

	def __init__(self, settings):
		PackageHandler.__init__(self, settings)
		# Specific buildd options
		# FIXME: decide how this is managed and packaged
		# variables to retrieve from the job object later
		self.dput_cfg = "/etc/pybit/client/dput.cf"
		if not settings["dry_run"] :
			os.chdir (settings["buildroot"])

def createPlugin (settings) :
	return DebianCrossClient (settings)
