#!/usr/bin/python

#       Copyright 2012:
#
#       Nick Davidson <nickd@toby-churchill.com>,
#       Simon Haswell <simonh@toby-churchill.com>,
#       Neil Williams <neilw@toby-churchill.com>,
#       James Bennet <github@james-bennet.com / James.Bennet@toby-churchill.com>

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

import jsonpickle
import os
import sys
from os.path import isfile
from pybitweb.bottle import Bottle,request,response

# TODO: Query the DB for this!
def check_auth(username, password):
    if username == 'admin' and password == 'pass':
        return True
    else:
        return False

def authenticate(msg_string = "Authenticate."):
	response.content_type = "application/json"
	message = {'message': msg_string}
	resp = jsonpickle.encode(message)
	response.status = "401 - Unauthorized"
	response.headers['WWW-Authenticate'] = 'Basic realm="PyBit"'

	return resp

def requires_auth(f):
    def decorated(*args, **kwargs):
        auth = request.auth
        if not auth:
              return authenticate()
        elif not check_auth(auth[0],auth[1]):
            response.status = "401 - Unauthorized"
            return authenticate("HTTP Authentication Failed.")
        else:
            return f(*args, **kwargs)
    return decorated

def load_from_cwd(filename):
    try:
        #print "DEBUG: Opening local file" , filename
        path = "%s/configs/%s" % (os.getcwd(),filename);

        if isfile(path): # exists
            settings_file = open(path, 'r')
            if settings_file: # can actually open it
                encoded_string = settings_file.read()
                settings = jsonpickle.decode(encoded_string )
                #print "DEBUG: Opened local config file", path
                return settings
            else:
                #print "ERROR: Error loading local file: ", path
                return None
        else:
            #print "ERROR: Error loading local file from path: ", path
            return None
    except Exception as e:
            raise Exception('Error loading local file:' + filename + str(e))
            return None

def load_from_etc(filename):
    try:
        #print "DEBUG: Opening config file" , filename
        path = "/etc/pybit/configs/%s" % (filename);

        if isfile(path): # exists
            settings_file = open(path, 'r')
            if settings_file: # can actually open it
                encoded_string = settings_file.read()
                settings = jsonpickle.decode(encoded_string )
                #print "DEBUG: Opened config file", path
                return settings
            else:
                #print "ERROR: Error loading config file: ", path
                return None
        else:
            #print "ERROR: Error loading config file from path: ", path
            return None
    except Exception as e:
            raise Exception('Error loading config file:' + filename + str(e))
            return None

def load_settings_from_file(filename):
    try:
        print "DEBUG: Loading settings file:" , filename, "....."
        localsettings = load_from_cwd(filename)
        globalsettings = load_from_etc(filename)

        #print "Local settings: " + repr(localsettings) + "Global settings: " + repr(globalsettings)

        if localsettings:
            print "DEBUG: Using local settings file"
            return localsettings
        elif globalsettings:
            print "DEBUG: Using system settings file"
            return globalsettings
        else:
            raise Exception # not loading settings is fatal, bail out
            return None
    except Exception as e:
            print ("FATAL ERROR: Error loading settings from: " + filename)
            sys.exit(-1)
            return False
