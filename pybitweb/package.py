#!/usr/bin/python

#       pybit-web
#       Copyright 2012:
#
#		Nick Davidson <nickd@toby-churchill.com>,
#		Simon Haswell <simonh@toby-churchill.com>,
#		Neil Williams <neilw@toby-churchill.com>,
#		James Bennet <github@james-bennet.com / James.Bennet@toby-churchill.com>
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

from bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect,request
import jsonpickle
from db import Database,myDb
from controller import Controller,buildController
from pybit.common import app


@app.route('/package', method='GET')
def get_all_packages():
	try:
		# Returning list of all packages
		packages = myDb.get_packages()
		encoded = jsonpickle.encode(packages)
		response.content_type = "application/json"
		return encoded
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@app.route('/package/<package_id:int>', method='GET')
def get_package_id(package_id):
	try:
		# Returns all information about a specific package
		res = myDb.get_package_id(package_id)

		# check results returned
		if res:
			encoded = jsonpickle.encode(res)
			response.content_type = "application/json"
			return encoded
		else:
			response.status = "404 - No package found with this ID."
			return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@app.route('/package', method='POST')
@app.route('/package', method='PUT')
def put_package():
	try:
		# Add a new package.
		version = request.forms.get('version')
		name = request.forms.get('name')

		if version and name:
			myDb.put_package(version,name)
		else:
			response.status = "400 - Required fields missing."
		return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@app.route('/package/<package_id:int>/delete', method='GET')
@app.route('/package/<package_id:int>', method='DELETE')
def delete_package(package_id):
	try:
		# Deletes a specific buildd
		# TODO: validation,security
		response.status = "202 - DELETE request recieved"
		myDb.delete_package(package_id)
		return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

#NEW: Have controller cancel all jobs for this package.
@app.route('/package/<package_id:int>/cancel', method='GET')
def cancel_package(package_id):
	try:
		response.status = "202 - CANCEL PACKAGE request recieved"

		buildController.cancel_package(package_id)
		return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@app.route('/package/list', method='GET') # TODO, filter by paramater (request.query.[x])
def get_packages_filtered():
	try:
		response.content_type = "application/json"
		#TODO - CODEME
		return "Returning packages by filter"
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

# Gets package versions (not instances!) by name.
@app.route('/package/details/:name', method='GET')
def get_package_versions(name):
	try:
		res = myDb.get_packages_byname(name)
		# check results returned
		if res:
			encoded = jsonpickle.encode(res)
			response.content_type = "application/json"
			return encoded
		else:
			response.status = "404 - No packages found with this name."
			return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@app.route('/package/details/:name/:version', method='GET')
def get_package_details(name,version):
	try:
		res = myDb.get_package_byvalues(name,version)
		# check results returned
		if res:
			encoded = jsonpickle.encode(res)
			response.content_type = "application/json"
			return encoded
		else:
			response.status = "404 - No package found with this name and version."
			return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None
