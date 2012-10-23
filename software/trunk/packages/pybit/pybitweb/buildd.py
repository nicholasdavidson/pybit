#!/usr/bin/python

from bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect,request
import jsonpickle
from db import db
import buildd

myDb = db()

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

@route('/buildd/<id:int>', method='GET')
def get_buildd_id(id):
	try:
		# Returns all information about a specific buildd
		res = myDb.get_buildd_id(id)

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

@route('/buildd/<id:int>', method='DELETE')
def delete_buildd_id(id):
	try:
		# Deletes a specific buildd
		# TODO: validation,security
		response.status = "202 - DELETE request recieved"
		res = myDb.delete_buildclient(id)
		return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/buildd/<id:int>/status', method='GET')
def get_buildd_status(id):
	try:
		response.content_type = "application/json"
		#TODO - CODEME
		return template("Returning status of buildd: {{id}}",id=id)
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/buildd/<id:int>/jobs', method='GET')
def get_buildd_jobs(id):
	try:
		#Returns jobs for specified buildd

		res = myDb.get_buildd_jobs(id)

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

@route('/buildd/<id:int>/:command', method='POST')
def post_command(id,command):
	try:
		response.status = "202 - Command sent"
		#TODO - CODEME
		return template("POSTed command '{{command}}' to buildd: {{id}}",id=id, command=command)
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None
