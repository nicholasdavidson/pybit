#!/usr/bin/python

from lib.bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect,request
import jsonpickle
from common.db import db
from common.models import arch,dist,format,status,suite
myDb = db()

@route('/arch', method='GET')
def get_arch():
	response.content_type = "application/json"
	#return list of arches
	arches = myDb.get_arches()
	encoded = jsonpickle.encode(arches)
	return encoded

@route('/arch/<id:int>', method='GET')
def get_arch_id(id):
	response.content_type = "application/json"
	# Returns all information about a specific arch
	res = myDb.get_arch_id(id)

	# check results returned
	if len(res) > 0:
		encoded = jsonpickle.encode(res)
		return encoded
	else:
		response.status = "404 - No arch found with this ID."
		return

@route('/arch', method='POST')
@route('/arch', method='PUT')
def put_arch():
	# Add a new arch. TODO: TESTME
	name = request.forms.get('name')

	if name:
		myDb.put_arch(name)
	else:
		response.status = "400 - Required fields missing."
	return

@route('/status', method='GET')
def get_statuses():
	response.content_type = "application/json"
	#return list of statuses
	statuses = myDb.get_statuses()
	encoded = jsonpickle.encode(statuses)
	return encoded

@route('/status/<id:int>', method='GET')
def get_status_id(id):
	response.content_type = "application/json"
	# Returns all information about a specific status
	res = myDb.get_status_id(id)

	# check results returned
	if len(res) > 0:
		encoded = jsonpickle.encode(res)
		return encoded
	else:
		response.status = "404 - No status found with this ID."
		return

@route('/status', method='POST')
@route('/status', method='PUT')
def put_status():
	# Add a new status. TODO: TESTME
	name = request.forms.get('name')

	if name:
		myDb.put_status(name)
	else:
		response.status = "400 - Required fields missing."
	return

@route('/dist', method='GET')
def get_dists():
	response.content_type = "application/json"
	#return list of distributions
	dists = myDb.get_dists()
	encoded = jsonpickle.encode(dists)
	return encoded

@route('/dist/<id:int>', method='GET')
def get_dist_id(id):
	response.content_type = "application/json"
	# Returns all information about a specific dist
	res = myDb.get_dist_id(id)

	# check results returned
	if len(res) > 0:
		encoded = jsonpickle.encode(res)
		return encoded
	else:
		response.status = "404 - No dist found with this ID."
		return

@route('/dist', method='POST')
@route('/dist', method='PUT')
def put_dist():
	# Add a new dist. TODO: TESTME
	name = request.forms.get('name')

	if name:
		myDb.put_dist(name)
	else:
		response.status = "400 - Required fields missing."
	return

@route('/format', method='GET')
def get_formats():
	response.content_type = "application/json"
	#return list of package formats
	formats = myDb.get_formats()
	encoded = jsonpickle.encode(formats)
	return encoded

@route('/format/<id:int>', method='GET')
def get_format_id(id):
	response.content_type = "application/json"
	# Returns all information about a specific format
	res = myDb.get_format_id(id)

	# check results returned
	if len(res) > 0:
		encoded = jsonpickle.encode(res)
		return encoded
	else:
		response.status = "404 - No format found with this ID."
		return

@route('/format', method='POST')
@route('/format', method='PUT')
def put_format():
	# Add a new format. TODO: TESTME
	name = request.forms.get('name')

	if name:
		myDb.put_format(name)
	else:
		response.status = "400 - Required fields missing."
	return

@route('/suite', method='GET')
def get_suites():
	response.content_type = "application/json"
	#return list of suites
	suites = myDb.get_suites()
	encoded = jsonpickle.encode(suites)
	return encoded

@route('/suite/<id:int>', method='GET')
def get_suite_id(id):
	response.content_type = "application/json"
	# Returns all information about a specific suite
	res = myDb.get_suite_id(id)

	# check results returned
	if len(res) > 0:
		encoded = jsonpickle.encode(res)
		return encoded
	else:
		response.status = "404 - No suite found with this ID."
		return

@route('/suite', method='POST')
@route('/suite', method='PUT')
def put_suite():
	# Add a new suite. TODO: TESTME
	name = request.forms.get('name')

	if name:
		myDb.put_suite(name)
	else:
		response.status = "400 - Required fields missing."
	return