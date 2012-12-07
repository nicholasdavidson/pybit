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

# If using with the git vcs handler, see also http://wiki.debian.org/GitSrc

# There could also be merit in renaming this as DebianSbuild and
# then supporting DebianSVN and DebianGit which would use
# svn-buildpackage & git-buildpackage respectively, instead of sbuild.

import os
import logging
import pybitclient
from buildclient import PackageHandler
from pybit.models import BuildRequest, checkValue

class DebianBuildClient(PackageHandler):
	dput_cfg = "" #FIXME
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

	def build_command_handler (self, buildreq, conn_data) :
		retval = None
		logfile = self.get_buildlog (self.settings["buildroot"], buildreq)
		# expect fakeroot debian/rules rules-target
		package_dir = os.path.join (self.settings["buildroot"],
				buildreq.get_suite(), buildreq.transport.method, buildreq.get_package())
		parts = buildreq.commands.split(' ')
		if len(parts) != 3 :
			retval = "failed-custom-command-len"
		if retval :
			return retval
		# only allow debian/rules targets, specified in full
		if parts[0] != "fakeroot" or parts[1] != "debian/rules" or parts[2] is None :
			retval = "failed-custom-command-parts"
		if retval :
			return retval
		# debian/rules targets must be run in the package_dir and
		# a command passed to schroot needs to be accessible inside the
		# chroot and therefore copied to ${HOME} so that schroot copies it again,
		# into the chroot itself.
		orig_sh = "/usr/share/pybitclient/sbuild-orig.sh"
		command = "(cp %s %s/sbuild-orig.sh ; schroot -n -u root -c %s -- %s/sbuild-orig.sh %s %s ; rm %s/sbuild-orig.sh)" % (orig_sh,
			self.settings["buildroot"], buildreq.get_suite(), self.settings["buildroot"], package_dir, parts[2], self.settings["buildroot"])
		if pybitclient.run_cmd (command, self.settings["dry_run"], logfile):
			retval = "custom-command-error"
		return retval

	def orig_source_handler (self, buildreq, conn_data) :
		retval = None
		logfile = self.get_buildlog (self.settings["buildroot"], buildreq)
		srcdir = os.path.join (self.settings["buildroot"],
				buildreq.get_suite(), buildreq.transport.method)
		version = buildreq.get_version()
		if '-' not in version :
			# native package, nothing to do for the orig source.
			return retval
		if self.settings["dry_run"] :
			logging.debug("I: %s (%s) is not a native package - need original source" % (buildreq.get_package(), version))
		offset = version.find('-')
		# strip the debian packaging part of the version string
		origversion = version[0:offset]
		origtar = os.path.join (srcdir, "%s_%s.orig.tar.gz" % (buildreq.get_package(), origversion))
		if os.path.isfile (origtar) :
			# have .gz
			return retval
		# check for .tar.bz2
		origtar = os.path.join (srcdir, "%s_%s.orig.tar.bz2" % (buildreq.get_package(), origversion))
		if os.path.isfile (origtar) :
			# have .bz2
			return retval
		# use a debian/watch file and uscan
		if os.path.isfile ("./debian/watch") :
			command = "(cd %s ; uscan --destdir ../ --repack --force-download --download-version %s)" % (os.path.join(srcdir,
				buildreq.get_package()), origversion)
			if pybitclient.run_cmd (command, self.settings["dry_run"], logfile):
				retval = "watch-failed"
				return retval
		# fall back to apt-get source
		else :
			command = "(cd ../ ; apt-get -d source %s/%s)" % (buildreq.get_package(), buildreq.get_suite())
			if pybitclient.run_cmd (command, self.settings["dry_run"], logfile):
				retval = "apt-get-source-failed"
		return retval

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
		# To check the build-dependencies in advance, we need to ensure the
		# chroot has an update apt-cache, so can't use apt-update option of
		# sbuild. The alternative is to update the apt-cache twice per build,
		# once for the dep check and once before the build. The choice depends
		# on whether two network trips are more efficient than rewriting the
		# lvm snapshot before even trying to do any build.
		if self.settings["use_lvm"] :
			update_name = "%s-source" % buildreq.get_suite()
		else :
			update_name = buildreq.get_suite()
		self.update_environment (update_name, buildreq, conn_data)
		# need an extra uscan stage to deal with non-native packages
		# this requires the upstream release to be accessible to the client.
		# i.e. unreleased versions of non-native packages cannot be built this way.
		# See #18 for the unreleased build support issue.
		if hasattr (buildreq, 'commands') and buildreq.commands :
			retval = self.build_command_handler (buildreq, conn_data)
		else : #61 - avoid dependency check if not using lvm
			if self.settings["use_lvm"] and (os.path.isdir(package_dir) or self.settings["dry_run"]) :
				control = os.path.join (package_dir, 'debian', 'control')
				dep_check = "/usr/lib/pbuilder/pbuilder-satisfydepends-classic --control"
				command = "schroot -u root -c %s -- %s %s" % (buildreq.get_suite(), dep_check, os.path.realpath(control))
				if pybitclient.run_cmd (command, self.settings["dry_run"], logfile):
					retval = "build-dep-wait"
			if not retval :
				retval = self.orig_source_handler (buildreq, conn_data)
			if not retval :
				dsc_file = "%s/%s_%s.dsc" % (srcdir, buildreq.get_package(), buildreq.get_version())
				if not os.path.exists (dsc_file) :
					command = "(cd %s && dpkg-buildpackage -nc -S -d -uc -us)" % (package_dir)
					if pybitclient.run_cmd (command, self.settings["dry_run"], logfile):
						retval = "build_dsc"
		if not retval :
			command = "sbuild -A -n -s -d %s %s/%s_%s.dsc" % (buildreq.get_suite(),
				srcdir, buildreq.get_package(), buildreq.get_version())
			ret = pybitclient.run_cmd (command, self.settings["dry_run"], logfile)
			if (ret == 3):
				retval = "build-dep-wait"
			elif (ret):
				retval = "build_binary"
		if not retval :
			changes = "%s/%s_%s_%s.changes" % (self.settings["buildroot"], buildreq.get_package(),
				buildreq.get_version(), buildreq.get_arch())
			if not self.settings["dry_run"] and not os.path.isfile (changes) :
				logging.debug("build_master: Failed to find %s file." % (changes))
				retval = "build_changes"
			if not retval and checkValue ('debsignkey', self.settings) :
				command = "debsign -k%s %s" % (self.settings['debsignkey'], changes)
				if pybitclient.run_cmd (command, self.settings["dry_run"], logfile):
					retval = "build_sign"
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
			# need an extra uscan stage to deal with non-native packages
			# this requires the upstream release to be accessible to the client.
			# i.e. unreleased versions of non-native packages cannot be built this way.
			# See #18 for the unreleased build support issue.
			if hasattr (buildreq, 'commands') and buildreq.commands :
				retval = self.build_command_handler (buildreq, conn_data)
			else :
				retval = self.orig_source_handler (buildreq, conn_data)
			command = "(cd %s ; dpkg-buildpackage -nc -S -d -uc -us)" % (package_dir)
			if pybitclient.run_cmd (command, self.settings["dry_run"], logfile):
				retval = "build_dsc"
			if not retval :
				command = "sbuild -n --apt-update -d %s %s/%s_%s.dsc" % (
					buildreq.get_suite(), srcdir,
					buildreq.get_package(), buildreq.get_version())
				ret = pybitclient.run_cmd (command, self.settings["dry_run"], logfile)
				if (ret == 3):
					retval = "build-dep-wait"
				elif (ret):
					retval = "build_binary"
			if not retval :
				changes = "%s/%s_%s_%s.changes" % (self.settings["buildroot"],
					buildreq.get_package(), buildreq.get_version(),
					buildreq.get_arch())
				if not self.settings["dry_run"] and not os.path.isfile (changes) :
					logging.debug ("build_slave: Failed to find %s file." % (changes))
					retval = "build_changes"
				if not retval and checkValue ('debsignkey', self.settings) :
					command = "debsign -k%s %s" % (self.settings['debsignkey'], changes)
					if pybitclient.run_cmd (command, self.settings["dry_run"], logfile):
						retval = "build_sign"
		else:
			retval = "Can't find build dir."
		if not retval :
			retval = "success"
		pybitclient.send_message (conn_data, retval)
		if retval == "success":
			return 0
		else :
			return 1

	def __init__(self, settings):
		PackageHandler.__init__(self, settings)
		# Specific buildd options
		# FIXME: decide how this is managed and packaged
		# variables to retrieve from the job object later
		self.dput_cfg = "/etc/pybit/client/dput.cf"
		if not settings["dry_run"] :
			os.chdir (settings["buildroot"])
