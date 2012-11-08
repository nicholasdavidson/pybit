#!/usr/bin/python

#       pybit-web
#       Copyright 2012:
#
#	Nick Davidson <nickd@toby-churchill.com>,
#	Simon Haswell <simonh@toby-churchill.com>,
#	Neil Williams <neilw@toby-churchill.com>,
#	James Bennet <github@james-bennet.com / James.Bennet@toby-churchill.com>
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

from pybitweb.bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect,request, hook, static_file
from pybitweb.db import Database,myDb
from pybitweb import handlers,lookups, buildd, job, package, packageinstance
from pybitweb.controller import Controller,buildController
from pybitweb.common import load_settings_from_file,app

settings = load_settings_from_file('web_settings.json')

#start the server
try:
	debug(settings['webserver_debug'])
	print("DEBUG: Starting " + settings['server_app'] + " on " + settings['webserver_protocol'] + settings['webserver_hostname'] + ":" + str(settings['webserver_port']) + ". Debug mode is: " + str(settings['webserver_debug']) + " and auto-reload is: " + str(settings['webserver_reloader']) + ".")
	run(app,server=settings['server_app'], host=settings['webserver_hostname'], port=settings['webserver_port'], reloader=settings['webserver_reloader'])
except Exception as e:
		raise Exception('Error starting web server: ' + str(e))
