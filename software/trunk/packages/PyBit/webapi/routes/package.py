#!/usr/bin/python

from lib.bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect,request
import jsonpickle
from common.db import db

myDb = db()

@route('/package', method='GET')
def get_all_packages():
	response.content_type = "application/json"
	# Returning list of all packages
	packages = myDb.get_packages()
	encoded = jsonpickle.encode(packages)
	return encoded

@route('/package/<id:int>', method='GET')
def get_package_id(id):
	response.content_type = "application/json"
	# Returns all information about a specific package
	res = myDb.get_package_id(id)

	# check results returned
	if len(res) > 0:
		encoded = jsonpickle.encode(res)
		return encoded
	else:
		response.status = "404 - No package found with this ID."
		return

@route('/package', method='POST')
@route('/package', method='PUT')
def put_package():
	# Add a new package. TODO: TESTME
	version = request.forms.get('version')
	name = request.forms.get('name')

	if version and name:
		myDb.put_package(version,name)
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