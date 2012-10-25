#!/usr/bin/python

from bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect,request
import jsonpickle
from db import Database,myDb

@route('/packageinstance', method='GET')
def get_all_packageinstances():
	try:
		# Returning list of all packageinstances
		packageinstances = myDb.get_packageinstances()
		encoded = jsonpickle.encode(packageinstances)
		response.content_type = "application/json"
		return encoded
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/packageinstance/<id:int>', method='GET')
def get_packageinstance_id(id):
	try:
		# Returns all information about a specific packageinstance
		res = myDb.get_packageinstance_id(id)

		# check results returned
		if res:
			encoded = jsonpickle.encode(res)
			response.content_type = "application/json"
			return encoded
		else:
			response.status = "404 - No packageinstance found with this ID."
			return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/packageinstance', method='POST')
@route('/packageinstance', method='PUT')
def put_packageinstance():
	try:
		# Add a new packageinstance.
		package_id = request.forms.get('package_id')
		arch_id = request.forms.get('arch_id')
		suite_id = request.forms.get('suite_id')
		dist_id = request.forms.get('dist_id')
		format_id =  request.forms.get('format_id')

		if package_id and arch_id  and suite_id  and dist_id and format_id:

			package = myDb.get_package_id(package_id)
			arch = myDb.get_arch_id(arch_id)
			suite = myDb.get_suite_id(suite_id)
			dist = myDb.get_dist_id(dist_id)
			format = myDb.get_format_id(format_id)

			myDb.put_packageinstance(package,arch,suite,dist,format,"false") # TODO: "false" or False?
		else:
			response.status = "400 - Required fields missing."
		return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/packageinstance/<id:int>', method='DELETE')
def delete_packageinstance(id):
	try:
		# Deletes a specific package instance
		# TODO: validation,security
		response.status = "202 - DELETE request recieved"
		res = myDb.delete_packageinstance(id)
		return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/packageinstance/list', method='GET')
def get_packageinstances_filtered():
	try:
		response.content_type = "application/json"
		#TODO - CODEME, filter by paramater (request.query.[x])
		return "Returning packageinstances by filter"
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/packageinstance/details/:name', method='GET')
def get_packageinstance_versions(name):
	try:
		#TODO - TESTME
		res = myDb.get_packageinstances_byname(name)
		# lists all instances of a package by name
		if res:
			encoded = jsonpickle.encode(res)
			response.content_type = "application/json"
			return encoded
		else:
			response.status = "404 - No packageinstances found with this name."
			return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None
