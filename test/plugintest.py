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
import pybit
from pybitclient.buildclient import PackageHandler, VersionControlHandler

handler_api = [ 'clean_source', 'fetch_source', 'get_srcdir', 'is_dry_run', 'method' ]
build_api   = [ 'build_master', 'build_slave', 'update_environment', 'upload' ]

def main():
	plugin = None
	vcs = None
	client = None
	plugins = []
	distros = {}
	handlers = {}
	plugin_dir = "/var/lib/pybit-client.d/"
	(settings, opened_path) = pybit.load_settings("client/client.conf")
	if not os.path.exists (plugin_dir):
		plugin_dir = "../pybitclient"
#		os.sys.exit (1)
	for name in os.listdir(plugin_dir):
		if name.endswith(".py"):
			plugins.append(name.strip('.py'))
	for name in plugins :
		if (name == "apt" or name == "git" or name == "crossdebian" or name == "buildclient" or name == "__init__"):
			continue
		print "checking plugin: %s" % name;
		plugin_path = [ plugin_dir ];
		fp, pathname, description = imp.find_module(name, plugin_path)
		try:
			mod = imp.load_module(name, fp, pathname, description)
			if not (hasattr(mod, 'createPlugin')) :
				print "Error: plugin path contains an unrecognised module."
				continue
			plugin = mod.createPlugin(settings)
			if (hasattr(plugin, 'get_distribution') and plugin.get_distribution() is not None) :
				client = plugin
				print dir(plugin)
			elif (hasattr(plugin, 'method') and plugin.method is not None) :
				vcs = plugin
				print dir(plugin)
			else :
				print "Error: plugin path contains an unrecognised module."
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
	if ('Debian' in distros):
		dist = distros["Debian"]
		print "Have a build client for %s" % dist.get_distribution()
	if ('svn' in handlers):
		print "Have a %s Handler for %s method" % (handlers['svn'].__class__.__name__, 'svn')
	return 0

if __name__ == '__main__':
	main()

