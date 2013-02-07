#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       buildd-test.py
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
import sys
import pybit
import logging
from pybitclient.subversion import SubversionClient
from pybitclient.git import GitClient
from pybitclient.debianclient import DebianBuildClient
from pybitclient.apt import AptClient
from pybitclient import PyBITClient
from pybit.models import BuildRequest, Transport, PackageInstance, Job, Arch, Suite, Package

def main():
	FORMAT = '%(asctime)s %(filename)s:%(lineno)d %(msg)s'
	logging.basicConfig( stream=sys.stderr, level=logging.DEBUG)
	logging.basicConfig( format=FORMAT )
	conffile = "%s/configs/client/client.conf" % (os.getcwd());
	testconf = "%s/buildd-test.conf" % (os.getcwd());
	if os.path.isfile (conffile):
		(settings, opened_path) = pybit.load_settings(conffile)
	else :
		(settings, opened_path) = pybit.load_settings("/etc/pybit/client/client.conf")
	build_client = PyBITClient(settings["host_arch"], settings["distribution"], settings["pkg_format"], settings["suites"], None, settings)

	if not os.path.isfile (testconf):
		print "E: Unable to find %s - no test data for this buildd" % (testconf)
		print "I: Copy /usr/share/pybitclient/buildd-test.conf and modify it for your available packages."
		return 1
	else :
		(test_options, opened_path) = pybit.load_settings(testconf)

	count = 0
	max_count = test_options["count"]
	tags = [ "vcs_id", "method_type", "suite", "package", "version",
		"architecture", "source", "uri", "pkg_format", "distribution", "role", "commands" ]
	svn_vcs = SubversionClient (settings)
	git_vcs = GitClient(settings)
	apt_src = AptClient(settings)
	client = DebianBuildClient (settings)

	while count < test_options["count"] and count < 10: # catch typos in the conf file
		count = count + 1
		for tag in tags :
			tag_run = "%s%s" % (tag, count)
			if tag_run not in test_options :
				print "E: missing config item in %s \"%s\"" % (testconf, tag_run)
				return -2
			if test_options[tag_run] == '' :
				test_options[tag_run] = None
			if tag == "vcs_id" :
				vcs_id = test_options[tag_run]
			elif tag == "method_type" :
				method_type = test_options[tag_run]
			elif tag == "suite" :
				suite = test_options[tag_run]
			elif tag == "package" :
				package = test_options[tag_run]
			elif tag == "version" :
				version = test_options[tag_run]
			elif tag == "architecture" :
				architecture = test_options[tag_run]
			elif tag == "source" :
				source = test_options[tag_run]
			elif tag == "uri" :
				uri = test_options[tag_run]
			elif tag == "pkg_format" :
				pkg_format = test_options[tag_run]
			elif tag == "distribution" :
				distribution = test_options[tag_run]
			elif tag == "commands" :
				commands = test_options[tag_run]
			elif tag == "role" :
				role = test_options[tag_run]
			else :
				print "E: unrecognised option: %s" % tag_run
				return -1
		logging.debug("I: starting test #%s (%s)" % (count, role))
		if commands is not None :
			logging.debug("I: test #%s requires a custom build command: '%s'" % (count, commands))
		test_arch = Arch(0, architecture)
		test_suite = Suite (0, suite)
		test_transport = Transport (0, method_type, uri, vcs_id)
		test_package = Package(0, version, package)
		test_packageinstance = PackageInstance(1, test_package, test_arch, None, test_suite, distribution, pkg_format, True)
		test_job =  Job(2, test_packageinstance,None)
		test_req = BuildRequest(test_job,test_transport,None)
		test_req.stamp_request()
		# clean up in case the last test failed.
		if (method_type == "svn") :
			svn_vcs.clean_source(test_req, None)
			svn_vcs.fetch_source (test_req, None)
		if (method_type == "git") :
			git_vcs.clean_source(test_req, None)
			git_vcs.fetch_source (test_req, None)
		if (method_type == "apt") :
			apt_src.clean_source(test_req, None)
			apt_src.fetch_source(test_req, None)
		if (role == "slave"):
			# runs the build with --apt-update
			client.build_slave (test_req, None)
		else :
			# runs update_environment first
			client.build_master (test_req, None)
		client.upload (test_req, None)
		if (method_type == "svn") :
			svn_vcs.clean_source(test_req, None)
		if (method_type == "git") :
			git_vcs.clean_source(test_req, None)
		if (method_type == "apt") :
			apt_src.clean_source(test_req, None)
	return 0

if __name__ == '__main__':
	main()
