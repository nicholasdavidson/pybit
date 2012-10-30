#!/usr/bin/python

from bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect,request
import jsonpickle
from db import Database,myDb
from controller import Controller,buildController


@route('/package', method='GET')
def get_all_packages():
	try:
		# Returning list of all packages
		packages = myDb.get_packages()
		encoded = jsonpickle.encode(packages)
		response.content_type = "application/json"
		return encoded
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/package/<id:int>', method='GET')
def get_package_id(id):
	try:
		# Returns all information about a specific package
		res = myDb.get_package_id(id)

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

@route('/package', method='POST')
@route('/package', method='PUT')
def put_package():
	try:
		# Add a new package.
		version = request.forms.get('version')
		name = request.forms.get('name')

		if version and name:
			myDb.put_package(version,name)
		else:
			response.status = "400 - Required fields missing."
		return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/package/<id:int>/delete', method='GET')
@route('/package/<id:int>', method='DELETE')
def delete_package(id):
	try:
		# Deletes a specific buildd
		# TODO: validation,security
		response.status = "202 - DELETE request recieved"
		res = myDb.delete_package(id)
		return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

#NEW: Have controller cancel all jobs for this package.
@route('/package/<id:int>/cancel', method='GET')
def cancel_package(id):
	try:
		response.status = "202 - CANCEL PACKAGE request recieved"

		buildController.cancel_package(id)
		return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/package/list', method='GET') # TODO, filter by paramater (request.query.[x])
def get_packages_filtered():
	try:
		response.content_type = "application/json"
		#TODO - CODEME
		return "Returning packages by filter"
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

# Gets package versions (not instances!) by name.
@route('/package/details/:name', method='GET')
def get_package_versions(name):
	try:
		#TODO - TESTME
		res = myDb.get_packages_byname(name)
		# check results returned
		if res:
			encoded = jsonpickle.encode(res)
			response.content_type = "application/json"
			return encoded
		else:
			response.status = "404 - No packages found with this name."
			return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/package/details/:name/:version', method='GET')
def get_package_details(name,version):
	try:
		#TODO - TESTME
		res = myDb.get_package_byvalues(name,version)
		# check results returned
		if res:
			encoded = jsonpickle.encode(res)
			response.content_type = "application/json"
			return encoded
		else:
			response.status = "404 - No package found with this name and version."
			return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None
