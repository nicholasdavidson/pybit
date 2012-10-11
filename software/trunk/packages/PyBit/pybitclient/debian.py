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
#import pybitclient
from common import run_cmd, send_message, get_settings, deb_package
#from pybitclient.common import get_settings

# Specific buildd options
# FIXME: decide how this is managed and packaged
if os.path.isfile ("client.conf"):
	options =  get_settings("client.conf")
else :
	options = get_settings("/etc/pybit/client/client.conf")
dput_opt = options["dput"]
buildroot = options["buildroot"]

# variables to retrieve from the job object later
dput_dest = "tcl"
dput_cfg = "/etc/pybit/dput.cf"

def update_environment (name):
	command = "schroot -u root -c " + name + "-- apt-get update > /dev/null 2>&1"
	if run_cmd (command, "failed", report_name, options["dry_run"]):
		return

def debian_build_master (srcdir, pkg):
	package_dir = srcdir + "/" + pkg.package
	builddir= buildroot + "/tmpbuilds/" + pkg.suite
	if os.path.isdir(package_dir) :
		os.chdir (package_dir)
		command = "dpkg-checkbuilddeps"
		if run_cmd (command, "build-dep-wait", report_name, options["dry_run"]):
			return
	command = "dpkg-buildpackage -S -d > /dev/null 2>&1"
	if run_cmd (command, "failed", report_name, options["dry_run"]):
		return
	command = "sbuild -A -s -d " + pkg.suite + srcdir + "/" + pkg.source + "_" + pkg.version + ".dsc";
	if run_cmd (command, "failed", report_name, options["dry_run"]):
		return
	changes = builddir + "/" + pkg.package + "_" + pkg.version + "_" + pkg.architecture + ".changes"
	if not os.path.isfile (changes) :
		pkg.msgtype = "failed"
		send_message (chan, pkg, report_name)
		return
	debian_upload (changes)


def debian_upload (changes):
	builddir= buildroot + "/tmpbuilds/" + pkg.suite
	command = "dput -c " + dput_cfg + " " + dput_opt + " " + dput_dest + " " + changes
	if run_cmd (command, "failed", report_name, options["dry_run"]):
		return
	pkg.msgtype = "uploaded"
	send_message (chan, pkg, report_name)


def debian_build_slave (srcdir, pkg):
	command = "sbuild -d " + pkg.suite + " " + pkg.source + "_" + pkg.version;
	if run_cmd (command, "failed", report_name, options["dry_run"]):
		return
	changes = builddir + "/" + pkg.package + "_" + pkg.version + "_" + pkg.architecture + ".changes"
	if not os.path.isfile (changes) :
		pkg.msgtype = "failed"
		send_message (chan, pkg, report_name)
		return
	debian_upload (changes)
