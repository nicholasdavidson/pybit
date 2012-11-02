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

@route('/packageinstance', method='GET')
def get_all_packageinstances():
	try:
		# Returning list of all packageinstances
		packageinstances = myDb.get_packageinstances()
		encoded = jsonpickle.encode(packageinstances)
		response.content_type = "application/json"
		return encoded
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/packageinstance/<packageinstance_id:int>', method='GET')
def get_packageinstance_id(packageinstance_id):
	try:
		# Returns all information about a specific packageinstance
		res = myDb.get_packageinstance_id(packageinstance_id)

		# check results returned
		if res:
			encoded = jsonpickle.encode(res)
			response.content_type = "application/json"
			return encoded
		else:
			response.status = "404 - No packageinstance found with this ID."
			return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/packageinstance', method='POST')
@route('/packageinstance', method='PUT')
def put_packageinstance():
	try:
		# Add a new packageinstance.
		package_id = request.forms.get('package_id')
		arch_id = request.forms.get('arch_id')
		suite_id = request.forms.get('suite_id')
		dist_id = request.forms.get('dist_id')
		format_id =  request.forms.get('format_id')

		if package_id and arch_id  and suite_id  and dist_id and format_id:

			package = myDb.get_package_id(package_id)
			arch = myDb.get_arch_id(arch_id)
			suite = myDb.get_suite_id(suite_id)
			dist = myDb.get_dist_id(dist_id)
			pkg_format = myDb.get_format_id(format_id)

			myDb.put_packageinstance(package,arch,suite,dist,pkg_format,"false") # TODO: "false" or False?
		else:
			response.status = "400 - Required fields missing."
		return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/packageinstance/<packageinstance_id:int>/delete', method='GET')
@route('/packageinstance/<packageinstance_id:int>', method='DELETE')
def delete_packageinstance(packageinstance_id):
	try:
		# Deletes a specific package instance
		# TODO: validation,security
		response.status = "202 - DELETE request recieved"
		myDb.delete_packageinstance(packageinstance_id)
		return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/packageinstance/list', method='GET')
def get_packageinstances_filtered():
	try:
		response.content_type = "application/json"
		#TODO - CODEME, filter by paramater (request.query.[x])
		return "Returning packageinstances by filter"
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/packageinstance/details/:name', method='GET')
def get_packageinstance_versions(name):
	try:
		res = myDb.get_packageinstances_byname(name)
		# lists all instances of a package by name
		if res:
			encoded = jsonpickle.encode(res)
			response.content_type = "application/json"
			return encoded
		else:
			response.status = "404 - No packageinstances found with this name."
			return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None
