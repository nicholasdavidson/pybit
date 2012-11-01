#!/usr/bin/python

from bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect,request
import jsonpickle
from db import Database,myDb
import buildd

@route('/buildd', method='GET')
def get_buildd():
	try:
		# Return list of BuildDs
		buildds = myDb.get_buildclients()
		encoded = jsonpickle.encode(buildds)
		response.content_type = "application/json"
		return encoded
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/buildd', method='POST')
@route('/buildd', method='PUT')
def put_buildd():
	try:
		# Register a new BuildD.
		name = request.forms.get('name')

		if name:
			myDb.put_buildclient(name)
		else:
			response.status = "400 - Required fields missing."
		return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/buildd/<buildd_id:int>', method='GET')
def get_buildd_id(buildd_id):
	try:
		# Returns all information about a specific buildd
		res = myDb.get_buildd_id(buildd_id)

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

@route('/buildd/<buildd_id:int>/delete', method='GET')
@route('/buildd/<buildd_id:int>', method='DELETE')
def delete_buildd_id(buildd_id):
	try:
		# Deletes a specific buildd
		# TODO: validation,security
		response.status = "202 - DELETE request recieved"
		myDb.delete_buildclient(buildd_id)
		return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/buildd/<buildd_id:int>/status', method='GET')
def get_buildd_status(buildd_id):
	try:
		response.content_type = "application/json"
		#TODO - CODEME
		return template("Returning status of buildd: {{buildd_id}}",buildd_id=buildd_id)
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/buildd/<buildclient_id:int>/jobs', method='GET')
def get_buildd_jobs(buildclient_id):
	try:
		#Returns jobs for specified buildd

		res = myDb.get_buildd_jobs(buildclient_id)

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

@route('/buildd/<buildd_id:int>/:command', method='POST')
def post_command(buildd_id,command):
	try:
		response.status = "202 - Command sent"
		#TODO - CODEME
		return template("POSTed command '{{command}}' to buildd: {{buildd_id}}",buildd_id=buildd_id, command=command)
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None
