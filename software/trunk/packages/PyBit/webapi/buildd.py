#!/usr/bin/python

from bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect
import jsonpickle
from db import db

myDb = db()

@route('/buildd', method='GET')
def get_buildd():
	response.content_type = "application/json"
	# Return list of BuildDs
	return jsonpickle.encode(myDb.get_buildclients());

@route('/buildd/<id:int>', method='GET')
def get_buildd_id(id):
	response.content_type = "application/json"
	# Returns all information about a specific buildd
	res = myDb.get_buildd_id(id)

	# check results returned
	if len(res) > 0:
		return jsonpickle.encode(res)
	else:
		response.status = "404 - No buildd found with this ID."
		return

@route('/buildd/<id:int>/status', method='GET')
def get_buildd_status(id):
	response.content_type = "application/json"
	#TODO - CODEME
	return template("Returning status of buildd: {{id}}",id=id)

@route('/buildd/<id:int>/jobs', method='GET')
def get_buildd_jobs(id):
	response.content_type = "application/json"
	#Returns jobs for specified buildd

	res = myDb.get_buildd_jobs(id)

	# check results returned
	if len(res) > 0:
		return jsonpickle.encode(res)
	else:
		response.status = "404 - No buildd found with this ID."
		return

	return template("Returning jobs for buildd: {{id}}",id=id)

@route('/buildd/<id:int>/:command', method='POST')
def post_command(id,command):
	response.status = "202 - Command recieved"
	#TODO - CODEME
	return template("POSTed command '{{command}}' to buildd: {{id}}",id=id, command=command)
