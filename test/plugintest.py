#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  plugintest.py
#
#  Copyright 2012 Neil Williams <codehelp@debian.org>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

import imp
import os
import logging
import sys
import unittest
import pybit
from pybitclient.buildclient import PackageHandler, VersionControlHandler

handler_api = [ 'clean_source', 'fetch_source', 'get_srcdir', 'is_dry_run', 'method' ]
build_api   = [ 'build_master', 'build_slave', 'update_environment', 'upload' ]

class TestClient(unittest.TestCase) :
	def setUp (self):
		return

	options = {}

	def test_01_plugin (self) :
		log = logging.getLogger( "testCase" )
		log.debug(" ")
		plugin = None
		vcs = None
		client = None
		plugins = []
		distros = {}
		handlers = {}
		plugin_dir = "/var/lib/pybit-client.d/"
		(settings, opened_path) = pybit.load_settings("client/client.conf")
		if not os.path.exists (plugin_dir):
			plugin_dir = os.path.join (os.getcwd(), "pybitclient/")
		self.assertTrue (os.path.isdir(plugin_dir))
		for name in os.listdir(plugin_dir):
			if name.endswith(".py"):
				plugins.append(name.strip('.py'))
		for name in plugins :
			if (name == "buildclient" or name == "__init__"):
				continue
			plugin_path = [ plugin_dir ];
			fp, pathname, description = imp.find_module(name, plugin_path)
			try:
				mod = imp.load_module(name, fp, pathname, description)
				self.assertTrue (mod)
				self.assertTrue (hasattr(mod, 'createPlugin'))
				plugin = mod.createPlugin(settings)
				self.assertTrue (plugin)
				self.assertTrue (hasattr(plugin, 'get_distribution') or hasattr(plugin, 'method'))
				if (hasattr(plugin, 'get_distribution') and plugin.get_distribution() is not None) :
					client = plugin
				elif (hasattr(plugin, 'method') and plugin.method is not None) :
					vcs = plugin
				else :
					self.assertTrue(False)
					continue
			finally:
				# Since we may exit via an exception, close fp explicitly.
				if fp:
					fp.close()
			if client:
				name = client.get_distribution()
				if (name not in distros) :
					distros[name] = client
			if vcs :
				if (vcs.method not in handlers) :
					handlers[vcs.method] = vcs;
		self.assertTrue (len(handlers.keys()) > 0)
		self.assertTrue (len(distros.keys()) > 0)


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

