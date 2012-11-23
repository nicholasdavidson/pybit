#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       pybitclient-test.py
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
import sys
import json
import unittest
# needs PYTHONPATH=.:..
import pybit
from pybitclient.buildclient import PackageHandler, VersionControlHandler
from pybitclient.debianclient import DebianBuildClient
from pybitclient.subversion import SubversionClient
from pybitclient.git import GitClient
from pybitclient.apt import AptClient

class TestClient(unittest.TestCase) :
	def setUp (self):
		return

	options = {}

	def test_01_client_config (self) :
		log = logging.getLogger( "testCase" )
		log.debug(" ")
		conffile = "%s/configs/client/client.conf" % (os.getcwd());
		self.assertTrue (os.path.isfile(conffile), "could not find %s" % conffile)
		log.debug("I: reading %s" % (os.path.relpath(conffile, os.getcwd())))
		(self.options, opened_path) = pybit.load_settings(conffile)
		if not "dry_run" in self.options :
			msg = "I: asserting dry_run for test cases"
			log.debug (msg)
			self.options["dry_run"] = True
		elif self.options["dry_run"] == False :
			msg = "I: overriding dry_run for test cases"
			log.debug (msg)
			self.options["dry_run"] = True
		else :
			msg = "I: dry_run already set."
			log.debug(msg)

	def test_02_build_client (self) :
		log = logging.getLogger( "testCase" )
		log.debug(" ")
		if not "dry_run" in self.options :
			msg = "I: asserting dry_run for test cases"
			log.debug (msg)
			self.options["dry_run"] = True
		base_client = PackageHandler(self.options)
		self.assertTrue (base_client)
		self.assertTrue (base_client.is_dry_run())
		deb_client = DebianBuildClient(self.options)
		self.assertTrue (deb_client)
		self.assertTrue (deb_client.is_dry_run())
		svn_client = SubversionClient(self.options)
		self.assertTrue (svn_client)
		self.assertTrue (svn_client.is_dry_run())
		apt_client = AptClient(self.options)
		self.assertTrue (apt_client)
		self.assertTrue (apt_client.is_dry_run())
		git_client = GitClient(self.options)
		self.assertTrue (git_client)
		self.assertTrue (git_client.is_dry_run())

def main():
	FORMAT = '%(msg)s'
	logging.basicConfig(format=FORMAT)
	logging.basicConfig( stream=sys.stderr )
	logging.getLogger( "testCase" ).setLevel( logging.DEBUG )
	suite = unittest.TestLoader().loadTestsFromTestCase(TestClient)
	runner = unittest.TextTestRunner(verbosity=2)
	res = runner.run(suite)
	if not res.wasSuccessful() :
		sys.exit (1)
	return 0

if __name__ == '__main__':
	main()
