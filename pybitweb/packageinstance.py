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
import common
from common import requires_auth

def get_packageinstance_app(settings, db):
	app = Bottle(config = { 'settings': settings, 'db': db})
	@app.route('/<packageinstance_id:int>/togglemaster/<master:int>', method='GET')
	def update_packageinstance_masterflag(packageinstance_id,master):
		try:
			app.config['db'].update_packageinstance_masterflag(packageinstance_id,master)
			response.status = "202 - Master flag changed."
			return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None
	@app.route('/', method='GET')
	def get_all_packageinstances():
		try:
			# Returning list of all packageinstances
			packageinstances = app.config['db'].get_packageinstances()
			encoded = jsonpickle.encode(packageinstances)
			response.content_type = "application/json"
			return encoded
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None
	
	@app.route('/<packageinstance_id:int>', method='GET')
	def get_packageinstance_id(packageinstance_id):
		try:
			# Returns all information about a specific packageinstance
			res = app.config['db'].get_packageinstance_id(packageinstance_id)
	
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
	
	@app.route('/', method='POST')
	@app.route('/', method='PUT')
	@requires_auth
	def put_packageinstance():
		try:
			# Add a new packageinstance.
			package = request.forms.get('package')
			version = request.forms.get('version')

			arch_id = request.forms.get('arch_id')
			suite_id = request.forms.get('suite_id')
			dist_id = request.forms.get('dist_id')
			format_id =  request.forms.get('format_id')
			slave = request.forms.get('slave')
	
			if not slave:
				slave = "false"
	
			if package and version and arch_id  and suite_id  and dist_id and format_id and slave:
	
				package_obj = app.config['db'].get_package_byvalues(package,version)[0]
				arch = app.config['db'].get_arch_id(arch_id)
				suite = app.config['db'].get_suite_id(suite_id)
				dist = app.config['db'].get_dist_id(dist_id)
				pkg_format = app.config['db'].get_format_id(format_id)
	
				app.config['db'].put_packageinstance(package_obj,arch,suite,dist,pkg_format,slave)
			else:
				response.status = "400 - Required fields missing."
			return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None
	
	@app.route('/<packageinstance_id:int>/delete', method='GET')
	@app.route('/<packageinstance_id:int>', method='DELETE')
	@requires_auth
	def delete_packageinstance(packageinstance_id):
		try:
			# Deletes a specific package instance
			response.status = "202 - DELETE request received"
			app.config['db'].delete_packageinstance(packageinstance_id)
			return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None
	
	@app.route('/list', method='GET')
	def get_packageinstances_filtered():
		try:
			response.content_type = "application/json"
			#TODO - CODEME, filter by parameter (request.query.[x])
			return "Returning packageinstances by filter"
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None
	
	@app.route('/details/:name', method='GET')
	def get_packageinstance_versions(name):
		try:
			res = app.config['db'].get_packageinstances_byname(name)
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
	return app
