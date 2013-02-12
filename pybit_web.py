#!/usr/bin/python

#	   pybit-web
#	   Copyright 2012:
#
#	Nick Davidson <nickd@toby-churchill.com>,
#	Simon Haswell <simonh@toby-churchill.com>,
#	Neil Williams <neilw@toby-churchill.com>,
#	James Bennet <github@james-bennet.com / James.Bennet@toby-churchill.com>
#
#	   This program is free software; you can redistribute it and/or modify
#	   it under the terms of the GNU General Public License as published by
#	   the Free Software Foundation; either version 2 of the License, or
#	   (at your option) any later version.
#
#	   This program is distributed in the hope that it will be useful,
#	   but WITHOUT ANY WARRANTY; without even the implied warranty of
#	   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	   GNU General Public License for more details.
#
#	   You should have received a copy of the GNU General Public License
#	   along with this program; if not, write to the Free Software
#	   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#	   MA 02110-1301, USA.

import jsonpickle
from pybitweb.db import Database
from pybitweb import lookups, buildd, job, package, packageinstance
from pybitweb.controller import Controller
import optparse
import pybitweb
from pybitweb import bottle
import pybit
import logging
import sys

META="PYBIT_WEB_"

if __name__ == '__main__':
	parser = optparse.OptionParser()
	#options we can override in the config file.
	groupConfigFile = optparse.OptionGroup(parser,
		"Config File Defaults","All the options which have defaults read from a config file.")
	parser.add_option_group(groupConfigFile)
	parser.add_option_group(groupConfigFile)

	parser.add_option("--config", dest="config", default="web/web.conf",
		help="Config file to read settings from, defaults to web.conf which will be read from configs/ and /etc/pybit/ in turn.",
		metavar=META + "CONF_FILE")

	parser.add_option("-v", dest="verbose", action="store_true", default=False,
		help="Turn on verbose messages.", metavar=META+"VERBOSE")
	(options, args) = parser.parse_args()
	(settings, opened_file) = pybit.load_settings(options.config)
	settings = pybit.merge_options(settings, groupConfigFile, options)
	
	FORMAT = '%(asctime)s %(filename)s:%(lineno)d %(msg)s'
	logging.basicConfig( stream=sys.stderr, level=logging.WARN)
	logging.basicConfig( format=FORMAT )
	
	myDb = Database(settings['db']) # singleton instance
	buildController = Controller(settings, myDb) # singleton instance - Needs access to both controller and web settings
#	try:
	app = pybitweb.get_app(settings, myDb, buildController)
	bottle.debug(options.verbose)
	bottle.run(app=app,
		server=settings['web']['app'],
		host=settings['web']['interface'],
		port=settings['web']['port'],
		reloader=settings['web']['reloader'])
