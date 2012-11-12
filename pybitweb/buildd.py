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

def get_buildd_app(settings, db):
	app = Bottle(config= {'settings' : settings, 'db' : db})
	@app.route('/', method='GET')
	def get_buildd():
		try:
			# Return list of BuildDs
			buildds = app.config['db'].get_buildclients()
			encoded = jsonpickle.encode(buildds)
			response.content_type = "application/json"
			return encoded
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None
	
	@app.route('/', method='POST')
	@app.route('/', method='PUT')
	@requires_auth
	def put_buildd():
		try:
			# Register a new BuildD.
			name = request.forms.get('name')
	
			if name:
				app.config['db'].put_buildclient(name)
			else:
				response.status = "400 - Required fields missing."
			return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None
	
	@app.route('/<buildd_id:int>', method='GET')
	def get_buildd_id(buildd_id):
		try:
			# Returns all information about a specific buildd
			res = app.config['db'].get_buildd_id(buildd_id)
	
			# check results returned
			if res:
				encoded = jsonpickle.encode(res)
				response.content_type = "application/json"
				return encoded
			else:
				response.status = "404 - No buildd found with this ID."
				return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None
	
	@app.route('/<buildd_id:int>/delete', method='GET')
	@app.route('/<buildd_id:int>', method='DELETE')
	@requires_auth
	def delete_buildd_id(buildd_id):
		try:
			# Deletes a specific buildd
			response.status = "202 - DELETE request received"
			app.config['db'].delete_buildclient(buildd_id)
			return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None
	
	@app.route('/<buildd_id:int>/status', method='GET')
	def get_buildd_status(buildd_id):
		try:
			response.content_type = "application/json"
			#TODO - CODEME
			return template("Returning status of buildd: {{buildd_id}}",buildd_id=buildd_id)
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None
	
	@app.route('/<buildclient_id:int>/jobs', method='GET')
	def get_buildd_jobs(buildclient_id):
		try:
			#Returns jobs for specified buildd
	
			res = app.config['db'].get_buildd_jobs(buildclient_id)
	
			# check results returned
			if res:
				encoded =  jsonpickle.encode(res)
				response.content_type = "application/json"
				return encoded
			else:
				response.status = "404 - No buildd found with this ID."
				return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None
	
	@app.route('/<buildd_id:int>/:command', method='POST')
	@requires_auth
	def post_command(buildd_id,command):
		try:
			response.status = "202 - Command sent"
			#TODO - CODEME
			return template("POSTed command '{{command}}' to buildd: {{buildd_id}}",buildd_id=buildd_id, command=command)
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None
	return app
