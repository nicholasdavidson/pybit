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
from db import Database
from controller import Controller
import bottle_basic_auth
from bottle_basic_auth import requires_auth
import psycopg2.errorcodes

def get_packages_app(settings, db, controller):
	app = Bottle()
	app.config={'settings':settings,'db':db, 'controller' : controller}

	@app.route('/', method='GET')
	@app.route('/page/<page:int>', method='GET')
	def get_all_packages(page = None):
		try:
			# Returning list of all packages
			if page:
				packages = app.config['db'].get_packages(page)
			else:
				packages = app.config['db'].get_packages()
			encoded = jsonpickle.encode(packages)
			response.content_type = "application/json"
			return encoded
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	@app.route('/count', method='GET')
	def get_count():
		#return count of packages
		count = app.config['db'].count_packages()
		encoded = jsonpickle.encode(count)
		response.content_type = "application/json"
		return encoded

	@app.route('/names', method='GET')
	def list_packagenames():
		try:
			# Returning list of all package names
			packages = app.config['db'].get_packagenames()
			encoded = jsonpickle.encode(packages)
			response.content_type = "application/json"
			return encoded
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	@app.route('/<package_id:int>', method='GET')
	def get_package_id(package_id):
		try:
			# Returns all information about a specific package
			res = app.config['db'].get_package_id(package_id)

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

	@app.route('/', method='POST')
	@app.route('/', method='PUT')
	@requires_auth
	def put_package():
		try:
			# Add a new package.
			version = request.forms.get('version')
			name = request.forms.get('name')

			if version and name:
				app.config['db'].put_package(version,name)
			else:
				response.status = "400 - Required fields missing."
			return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	@app.route('/<package_id:int>/delete', method='GET')
	@app.route('/<package_id:int>', method='DELETE')
	@requires_auth
	def delete_package(package_id):
		try:
			# Deletes a specific buildd
			retval = app.config['db'].delete_package(package_id)

			if(retval == True):
				response.status = "200 DELETE OK"
			elif(retval == False):
				response.status = "404 Cannot DELETE"
			elif(retval == "23503"):
				response.status = "409 " + str(errorcodes.lookup(retval))
			else:
				response.status = "500 " + str(errorcodes.lookup(retval))

			return response.status
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	#NEW: Have controller cancel all jobs for this package.
	@app.route('/<package_id:int>/cancel', method='GET')
	@requires_auth
	def cancel_package(package_id):
		try:
			response.status = "202 - CANCEL PACKAGE request received"

			app.config['controller'].cancel_package(package_id)
			return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	@app.route('/list', method='GET') # TODO, filter by parameter (request.query.[x])
	def get_packages_filtered():
		try:
			response.content_type = "application/json"
			#TODO - CODEME
			return "Returning packages by filter"
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	# Gets package versions (not instances!) by name.
	@app.route('/details/:name', method='GET')
	def get_package_versions(name):
		try:
			res = app.config['db'].get_packages_byname(name)
			# check results returned
			if res:
				encoded = jsonpickle.encode(res)
				response.content_type = "application/json"
				return encoded
			else:
				response.status = "404 No packages found with this name."
				return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	# Gets package versions (not instances!) by name.
	@app.route('/<package_id:int>/active', method='GET')
	def get_package_active_jobs(package_id):
		try:
			response.content_type = "text/plain"
			return str(app.config['db'].check_package_has_unfinished_jobs(package_id))
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	@app.route('/details/:name/:version', method='GET')
	def get_package_details(name,version):
		try:
			res = app.config['db'].get_package_byvalues(name,version)
			# check results returned
			if res:
				encoded = jsonpickle.encode(res)
				response.content_type = "application/json"
				return encoded
			else:
				response.status = "404 No package found with this name and version."
				return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None
	return app
