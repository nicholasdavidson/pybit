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
import pybitclient
from pybitclient.debian import DebianBuildClient
from pybitclient.subversion import SubversionClient

class TestClient(unittest.TestCase) :
	def setUp (self):
		return

	options = {}

	def test_01_client_config (self) :
		log= logging.getLogger( "testCase" )
		log.debug("\n")
		conffile = "%s/pybitclient/client.conf" % (os.getcwd());
		if os.path.isfile (conffile):
			log.debug("I: reading %s" % (os.path.relpath(conffile, os.getcwd())))
			self.options = pybitclient.get_settings(conffile)
		elif os.path.isfile ("/etc/pybit/client/client.conf") :
			conffile = "/etc/pybit/client/client.conf";
			log.debug("I: reading %s" % (conffile))
			self.options = pybitclient.get_settings(conffile)
		else :
			log.debug("I: unable to find config file.")
		if not "dry_run" in self.options :
			msg = "I: dry_run not set in options"
			log.debug (msg)
			self.options["dry_run"] = True
		else :
			msg = "I: dry_run already set."
			log.debug(msg)

	def test_02_build_client (self) :
		log= logging.getLogger( "testCase" )
		log.debug("\n")
		deb_client = DebianBuildClient()
		svn_client = SubversionClient()
		msg = "I: srcdir = %s" % (svn_client.get_srcdir())
		log.debug(msg)

if __name__ == '__main__':
	FORMAT = '%(msg)s'
	logging.basicConfig(format=FORMAT)
	logging.basicConfig( stream=sys.stderr )
	logging.getLogger( "testCase" ).setLevel( logging.DEBUG )
	suite = unittest.TestLoader().loadTestsFromTestCase(TestClient)
	unittest.TextTestRunner(verbosity=2).run(suite)
