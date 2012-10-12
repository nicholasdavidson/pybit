#!/usr/bin/python

from bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect,request
import jsonpickle
from common.db import db

myDb = db()

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
		if len(res) > 0:
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
		# Add a new package. TODO: TESTME
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

@route('/package/list', method='GET') # TODO, filter by paramater (request.query.[x])
def get_packages_filtered():
	try:
		response.content_type = "application/json"
		#TODO - CODEME
		return "Returning packages by filter"
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/package/details/:name:', method='GET')
def get_package_versions(name):
	try:
		response.content_type = "application/json"
		#TODO - CODEME
		return template("Returning versions for package {{name}}",name=name)
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/package/details/:name:/:version', method='GET')
def get_package_details(name,version):
	try:
		response.content_type = "application/json"
		#TODO - CODEME
		return template("Returning details for package {{name}} v{{version}}",name=name, version=version)
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None
