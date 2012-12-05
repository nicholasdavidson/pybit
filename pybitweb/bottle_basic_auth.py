#!/usr/bin/python

#   Copyright 2012:
#
#   Nick Davidson <nickd@toby-churchill.com>,
#   Simon Haswell <simonh@toby-churchill.com>,
#   Neil Williams <neilw@toby-churchill.com>,
#   James Bennet <github@james-bennet.com / James.Bennet@toby-churchill.com>

#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#   MA 02110-1301, USA.

import jsonpickle
import os
import sys
import pybit

from os.path import isfile
from pybitweb.bottle import Bottle,request,response

# TODO: This is a huge bodge. Query the DB for this!
def check_auth(username, password):
	# Load from local settings file in configs, or if not, from system settings in etc.
	(auth_settings,path) = pybit.load_settings("web/web.conf")
	if not auth_settings:
		# Cant load settings
		return False

	# Check credentials
	if auth_settings['web']['username'] == username and auth_settings['web']['password'] == password:
		return True
	else:
		return False

def authenticate():
	response.content_type = "text/html"
	response.status = "401 - Unauthorized"
	response.headers['WWW-Authenticate'] = 'Basic realm="PyBit"'
	return "401 - Unauthorized"

def requires_auth(f):
	def decorated(*args, **kwargs):
		auth = request.auth
		if not auth:
			  return authenticate()
		elif not check_auth(auth[0],auth[1]):
			response.status = "401 - Unauthorized"
			return authenticate()
		else:
			return f(*args, **kwargs)
	return decorated
