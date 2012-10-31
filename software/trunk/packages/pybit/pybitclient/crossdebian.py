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
import pybitclient
from buildclient import PackageHandler
from pybit.models import BuildRequest

class DebianBuildClient(PackageHandler):
	options = {}
	dput_cfg = ""
	dput_dest = ""

	def update_environment(self,name,pkg, conn_data):
		retval = "success"
		command = "schroot -u root -c %s -- apt-get update > /dev/null 2>&1" % (name)
		if not pybitclient.run_cmd (command, self.options["dry_run"]) :
			retval = "build_update"
		pybitclient.send_message (conn_data, retval)

	def build_master (self, buildreq, conn_data):
		retval = None
		if (not isinstance(buildreq, BuildRequest)):
			print "E: not able to identify package name."
			retval = "misconfigured"
			pybitclient.send_message (conn_data, retval)
			return
		srcdir = os.path.join (self.options["buildroot"],
				buildreq.get_suite(), buildreq.transport.method)
		package_dir = "%s/%s" % (srcdir, buildreq.get_package())
		command = "(cd %s ; dpkg-buildpackage -S -d -uc -us)" % (package_dir)
		if not pybitclient.run_cmd (command, self.options["dry_run"]):
			retval = "build-dep-wait"
		if not retval :
			command = "sbuild --debbuildopt=\"-a%s\" --setup-hook=\"/usr/bin/sbuild-cross.sh\" --arch=%s -A -s -d %s %s/%s_%s.dsc" %
				(pkg.architecture, pkg.architecture, pkg.suite, srcdir, pkg.source, pkg.version)
			if not pybitclient.run_cmd (command, self.options["dry_run"]):
				retval = "build_binary"
		if not retval :
			changes = "%s/%s_%s_%s.changes" % (srcdir, buildreq.get_package(),
				buildreq.get_version(), buildreq.get_arch())
			if not os.path.isfile (changes) :
				print "Failed to find %s file." % (changes)
				retval = "build_changes"
		if not retval :
			retval = "success"
		pybitclient.send_message (conn_data, retval)

	def upload (self, buildreq, conn_data):
		retval = None
		srcdir = os.path.join (self.options["buildroot"],
				buildreq.get_suite(), buildreq.transport.method)
		changes = "%s/%s_%s_%s.changes" % (srcdir, buildreq.get_package(),
			buildreq.get_version(), buildreq.get_arch())
		if not os.path.isfile (changes) :
			print "Failed to find %s file." % (changes)
			retval = "upload_changes"
		if not retval :
			command = "dput -c %s %s %s %s" % (self.dput_cfg,
				self.options["dput"], self.options["dput_dest"], changes)
			if not pybitclient.run_cmd (command, self.options["dry_run"]):
				retval = "upload_fail"
		if not retval :
			retval = "success"
		pybitclient.send_message (conn_data, retval)

	def build_slave (self, buildreq, conn_data):
		retval = None
		srcdir = os.path.join (self.options["buildroot"],
				buildreq.get_suite(), buildreq.transport.method)
		package_dir = "%s/%s" % (srcdir, buildreq.get_package())
		if os.path.isdir(package_dir) :
			command = "(cd %s ; dpkg-buildpackage -S -d -uc -us)" % package_dir
			if not pybitclient.run_cmd (command, self.options["dry_run"]):
				retval = "build_dsc"
			if not retval :
				command = "sbuild --apt-update -d %s %s/%s_%s.dsc" % (
					buildreq.get_suite(), srcdir,
					buildreq.get_package(), buildreq.get_version())
				if not pybitclient.run_cmd (command, self.options["dry_run"]):
					retval = "build_binary"
			if not retval :
				changes = "%s/%s_%s_%s.changes" % (srcdir,
					buildreq.get_package(), buildreq.get_version(),
					buildreq.get_arch())
				if not os.path.isfile (changes) :
					print "Failed to find %s file." % (changes)
					retval = "build_changes"
		if not retval :
			retval = "success"
		pybitclient.send_message (conn_data, retval)

	def __init__(self):
		try:
			PackageHandler.__init__(self)
			# Specific buildd options
			# FIXME: decide how this is managed and packaged
			self.options =  pybitclient.get_settings(self)
			if len(self.options) > 0 :
				dput_opt = self.options["dput"]
				buildroot = self.options["buildroot"]
			else :
				self.options["dry_run"] = True
			# variables to retrieve from the job object later
			self.dput_dest = "tcl"
			self.dput_cfg = "/etc/pybit/client/dput.cf"
		except Exception as e:
			raise Exception('Error constructing debian build client: ' + str(e))
			return
