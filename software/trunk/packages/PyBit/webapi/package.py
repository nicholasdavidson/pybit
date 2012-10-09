#!/usr/bin/python

from bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect
import jsonpickle
from db import db

myDb = db()

@route('/package', method='GET')
def get_all_packages():
	response.content_type = "application/json"
	# Returning list of all packages
	return jsonpickle.encode(myDb.get_packages());

@route('/package', method='PUT')
def put_package():
	# Add a new package. TODO: TESTME
	id = request.forms.get('id')
	version = request.forms.get('version')
	name = request.forms.get('name')

	if id and version and name:
		myDb.put_package(id,version,name)
	else:
		response.status = "400 - Required fields missing."
	return

@route('/package/<id:int>', method='DELETE')
def delete_package(id):
	# Deletes a specific buildd
	# TODO: validation,security
	response.status = "202 - DELETE request recieved"
	res = myDb.delete_package(id)
	return

@route('/package/list', method='GET') # TODO, filter by paramater (request.query.[x])
def get_packages_filtered():
	response.content_type = "application/json"
	#TODO - CODEME
	return "Returning packages by filter"

@route('/package/details/:name:', method='GET')
def get_package_versions(name):
	response.content_type = "application/json"
	#TODO - CODEME
	return template("Returning versions for package {{name}}",name=name)

@route('/package/details/:name:/:version', method='GET')
def get_package_details(name,version):
	response.content_type = "application/json"
	#TODO - CODEME
	return template("Returning details for package {{name}} v{{version}}",name=name, version=version)
