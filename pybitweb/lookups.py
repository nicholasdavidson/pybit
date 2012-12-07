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
from pybit.models import Arch,Dist,Format,Status,Suite,SuiteArch
import bottle_basic_auth
from bottle_basic_auth import requires_auth

def get_arch_app(settings, db):
	app = Bottle()
	app.config={'settings':settings, 'db':db}

	@app.route('/', method='GET')
	@app.route('/page/<page:int>', method='GET')
	def get_arch(page = None):
		#return list of arches
		if page:
			arches = app.config['db'].get_arches(page)
		else:
			arches = app.config['db'].get_arches()
		encoded = jsonpickle.encode(arches)
		response.content_type = "application/json"
		return encoded

	@app.route('/count', method='GET')
	def get_count():
		#return count of arches
		count = app.config['db'].count_arches()
		encoded = jsonpickle.encode(count)
		response.content_type = "application/json"
		return encoded

	@app.route('/<arch_id:int>', method='GET')
	def get_arch_id(arch_id):

			# Returns all information about a specific arch
		res = app.config['db'].get_arch_id(arch_id)

			# check results returned
		if res:
			encoded = jsonpickle.encode(res)
			response.content_type = "application/json"
			return encoded
		else:
			response.status = "404 - No arch found with this ID."
			return

	@app.route('/', method='POST')
	@app.route('/', method='PUT')
	@requires_auth
	def put_arch():
		try:
			# Add a new arch.
			name = request.forms.get('name')

			if name:
				app.config['db'].put_arch(name)
			else:
				response.status = "400 - Required fields missing."
			return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	@app.route('/<arch_id:int>/delete', method='GET')
	@app.route('/<arch_id:int>', method='DELETE')
	@requires_auth
	def delete_arch(arch_id):
		try:
			# Deletes a specific arch
			response.status = "202 - DELETE request received"
			app.config['db'].delete_arch(arch_id)
			return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None
	return app

def get_suitearch_app(settings, db):
	app = Bottle()
	app.config={'settings':settings, 'db':db}

	@app.route('/', method='GET')
	def get_suitearch():
		try:
			#return list of suitearch
			suitearches = app.config['db'].get_suitearches()
			encoded = jsonpickle.encode(suitearches)
			response.content_type = "application/json"
			return encoded
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	@app.route('/count', method='GET')
	def get_count():
		#return count of suitearches
		count = app.config['db'].count_suitearches()
		encoded = jsonpickle.encode(count)
		response.content_type = "application/json"
		return encoded


	@app.route('/<suitearch_id:int>', method='GET')
	def get_suitearch_id(suitearch_id):
		try:
			# Returns all information about a specific suitearch
			res = app.config['db'].get_suitearch_id(suitearch_id)

			# check results returned
			if res:
				encoded = jsonpickle.encode(res)
				response.content_type = "application/json"
				return encoded
			else:
				response.status = "404 - No suitearch found with this ID."
				return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	@app.route('/', method='POST')
	@app.route('/', method='PUT')
	@requires_auth
	def put_suitearch():
		# Add a new suitearch.
		suite_id = request.forms.get('suite_id')
		arch_id =  request.forms.get('arch_id')
		master_weight =  request.forms.get('master_weight')

		if not master_weight or master_weight == "":
			master_weight = 0

		if suite_id and arch_id:
			app.config['db'].put_suitearch(suite_id,arch_id,master_weight)
		else:
			response.status = "400 - Required fields missing."
		return

	@app.route('/<suitearch_id:int>/delete', method='GET')
	@app.route('/<suitearch_id:int>', method='DELETE')
	@requires_auth
	def delete_suitearch(suitearch_id):
		try:
			# Deletes a specific suitearch
			response.status = "202 - DELETE request received"
			app.config['db'].delete_suitearch(suitearch_id)
			return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None
	return app

def get_status_app(settings, db):
	app = Bottle()
	app.config={'settings':settings, 'db':db}

	@app.route('/', method='GET')
	@app.route('/page/<page:int>', method='GET')
	def get_statuses(page = None):
		try:
			#return list of statuses
			if page:
				statuses = app.config['db'].get_statuses(page)
			else:
				statuses = app.config['db'].get_statuses()
			encoded = jsonpickle.encode(statuses)
			response.content_type = "application/json"
			return encoded
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	@app.route('/count', method='GET')
	def get_count():
		#return count of statuses
		count = app.config['db'].count_statuses()
		encoded = jsonpickle.encode(count)
		response.content_type = "application/json"
		return encoded

	@app.route('/<status_id:int>', method='GET')
	def get_status_id(status_id):
		try:
			# Returns all information about a specific status
			res = app.config['db'].get_status_id(status_id)

			# check results returned
			if res:
				encoded = jsonpickle.encode(res)
				response.content_type = "application/json"
				return encoded
			else:
				response.status = "404 - No status found with this ID."
				return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	@app.route('/', method='POST')
	@app.route('/', method='PUT')
	@requires_auth
	def put_status():
		try:
			# Add a new status.
			name = request.forms.get('name')

			if name:
				app.config['db'].put_status(name)
			else:
				response.status = "400 - Required fields missing."
			return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	@app.route('/<status_id:int>/delete', method='GET')
	@app.route('/<status_id:int>', method='DELETE')
	@requires_auth
	def delete_status(status_id):
		try:
			# Deletes a specific status
			response.status = "202 - DELETE request received"
			app.config['db'].delete_status(status_id)
			return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None
	return app

def get_dist_app(settings, db):
	app = Bottle()
	app.config={'settings':settings, 'db':db}

	@app.route('/', method='GET')
	@app.route('/page/<page:int>', method='GET')
	def get_dists(page = None):
		try:
			#return list of distributions
			if page:
				dists = app.config['db'].get_dists(page)
			else:
				dists = app.config['db'].get_dists(page)
			encoded = jsonpickle.encode(dists)
			response.content_type = "application/json"
			return encoded
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	@app.route('/count', method='GET')
	def get_count():
		#return count of dists
		count = app.config['db'].count_dists()
		encoded = jsonpickle.encode(count)
		response.content_type = "application/json"
		return encoded

	@app.route('/<dist_id:int>', method='GET')
	def get_dist_id(dist_id):
		try:
			# Returns all information about a specific dist
			res = app.config['db'].get_dist_id(dist_id)

			# check results returned
			if res:
				encoded = jsonpickle.encode(res)
				response.content_type = "application/json"
				return encoded
			else:
				response.status = "404 - No dist found with this ID."
				return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	@app.route('/', method='POST')
	@app.route('/', method='PUT')
	@requires_auth
	def put_dist():
		try:
			# Add a new dist.
			name = request.forms.get('name')

			if name:
				app.config['db'].put_dist(name)
			else:
				response.status = "400 - Required fields missing."
			return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	@app.route('/<dist_id:int>/delete', method='GET')
	@app.route('/<dist_id:int>', method='DELETE')
	@requires_auth
	def delete_dist(dist_id):
		try:
			# Deletes a specific dist
			response.status = "202 - DELETE request received"
			app.config['db'].delete_dist(dist_id)
			return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None
	return app

def get_format_app(settings, db):
	app = Bottle()
	app.config={'settings':settings, 'db':db}

	@app.route('/', method='GET')
	@app.route('/page/<page:int>', method='GET')
	def get_formats(page = None):
		try:
			#return list of package formats
			if page:
				formats = app.config['db'].get_formats(page)
			else:
				formats = app.config['db'].get_formats()
			encoded = jsonpickle.encode(formats)
			response.content_type = "application/json"
			return encoded
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	@app.route('/count', method='GET')
	def get_count():
		#return count of formats
		count = app.config['db'].count_formats()
		encoded = jsonpickle.encode(count)
		response.content_type = "application/json"
		return encoded

	@app.route('/<format_id:int>', method='GET')
	def get_format_id(format_id):
		try:
			# Returns all information about a specific format
			res = app.config['db'].get_format_id(format_id)

			# check results returned
			if res:
				encoded = jsonpickle.encode(res)
				response.content_type = "application/json"
				return encoded
			else:
				response.status = "404 - No format found with this ID."
				return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	@app.route('/', method='POST')
	@app.route('/', method='PUT')
	@requires_auth
	def put_format():
		try:
			# Add a new format.
			name = request.forms.get('name')

			if name:
				app.config['db'].put_format(name)
			else:
				response.status = "400 - Required fields missing."
			return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	@app.route('/<format_id:int>/delete', method='GET')
	@app.route('/<format_id:int>', method='DELETE')
	@requires_auth
	def delete_format(format_id):
		try:
			# Deletes a specific format
			response.status = "202 - DELETE request received"
			app.config['db'].delete_format(format_id)
			return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None
	return app
def get_suite_app(settings, db):
	app = Bottle()
	app.config={'settings':settings, 'db':db}

	@app.route('/', method='GET')
	@app.route('/page/<page:int>', method='GET')
	def get_suites(page = None):
		try:
			#return list of suites
			if page:
				suites = app.config['db'].get_suites(page)
			else:
				suites = app.config['db'].get_suites()
			encoded = jsonpickle.encode(suites)
			response.content_type = "application/json"
			return encoded
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	@app.route('/count', method='GET')
	def get_count():
		#return count of suites
		count = app.config['db'].count_suites()
		encoded = jsonpickle.encode(count)
		response.content_type = "application/json"
		return encoded

	@app.route('/<suite_id:int>', method='GET')
	def get_suite_id(suite_id):
		try:
			# Returns all information about a specific suite
			res = app.config['db'].get_suite_id(suite_id)

			# check results returned
			if res:
				encoded = jsonpickle.encode(res)
				response.content_type = "application/json"
				return encoded
			else:
				response.status = "404 - No suite found with this ID."
				return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	@app.route('/', method='POST')
	@app.route('/', method='PUT')
	@requires_auth
	def put_suite():
		try:
			# Add a new suite.
			name = request.forms.get('name')

			if name:
				app.config['db'].put_suite(name)
			else:
				response.status = "400 - Required fields missing."
			return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	@app.route('/<suite_id:int>/delete', method='GET')
	@app.route('/<suite_id:int>', method='DELETE')
	@requires_auth
	def delete_suite(suite_id):
		try:
			# Deletes a specific suite
			response.status = "202 - DELETE request received"
			app.config['db'].delete_suite(suite_id)
			return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None
	return app
