#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       debian.py
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
import json
import pybitclient
from buildclient import PackageHandler

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

	def build_master (self, srcdir, pkg, conn_data):
		retval = None
		if (not hasattr(pkg, 'package')):
			print "E: not able to identify package name."
			retval = "misconfigured"
			pybitclient.send_message (conn_data, retval)
			return
		package_dir = "%s/%s" % (srcdir, pkg.package)
		# FIXME: doesn't make sense to run dpkg-checkbuilddeps outside the chroot!
		if os.path.isdir(package_dir) :
			control = os.path.join (package_dir, 'debian', 'control')
			dep_check = "/usr/lib/pbuilder/pbuilder-satisfydepends-classic --control"
			command = "schroot -u root -c %s -- %s %s" % (pkg.suite, dep_check, os.path.realpath(control))
			if not pybitclient.run_cmd (command, self.options["dry_run"]):
				retval = "build-dep-wait"
		if not retval :
			command = "(cd %s ; dpkg-buildpackage -S -d -uc -us)" % (package_dir)
			if not pybitclient.run_cmd (command, self.options["dry_run"]):
				retval = "build_dsc"
		if not retval :
			command = "sbuild -A -s -d %s %s/%s_%s.dsc" % (pkg.suite, srcdir, pkg.source, pkg.version)
			if not pybitclient.run_cmd (command, self.options["dry_run"]):
				retval = "build_binary"
		if not retval :
			changes = "%s/%s_%s_%s.changes" % (srcdir, pkg.package, pkg.version, pkg.architecture)
			if not os.path.isfile (changes) :
				print "Failed to find %s file." % (changes)
				retval = "build_changes"
		if not retval :
			retval = "success"
		pybitclient.send_message (conn_data, retval)

	def upload (self, dirname, changes, pkg, conn_data):
		retval = None
		changes = "%s/%s_%s_%s.changes" % (srcdir, pkg.package, pkg.version, pkg.architecture)
		if not os.path.isfile (changes) :
			print "Failed to find %s file." % (changes)
			retval = "upload_changes"
		if not retval :
			changes_path = os.path.join (dirname, changes)
			command = "dput -c %s %s %s %s" % (self.dput_cfg, self.options["dput"], self.dput_dest, changes_path)
			if not pybitclient.run_cmd (command, self.options["dry_run"]):
				retval = "upload_fail"
		if not retval :
			retval = "success"
		pybitclient.send_message (conn_data, retval)

	def build_slave (self, srcdir, pkg, conn_data):
		retval = None
		package_dir = "%s/%s" % (srcdir, pkg.package)
		if os.path.isdir(package_dir) :
			command = "(cd %s ; dpkg-buildpackage -S -d -uc -us)" % package_dir
			if not pybitclient.run_cmd (command, self.options["dry_run"]):
				retval = "build_dsc"
			if not retval :
				command = "sbuild --apt-update -d %s %s/%s_%s.dsc" % (pkg.suite, srcdir, pkg.source, pkg.version)
				if not pybitclient.run_cmd (command, self.options["dry_run"]):
					retval = "build_binary"
			if not retval :
				changes = "%s/%s_%s_%s.changes" % (srcdir, pkg.package, pkg.version, pkg.architecture)
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
