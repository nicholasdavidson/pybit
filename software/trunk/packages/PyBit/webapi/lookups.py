#!/usr/bin/python

from bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect
import jsonpickle
from db import db

myDb = db()

# TODO: PUT methods

@route('/arch', method='GET')
def get_arch():
	response.content_type = "application/json"
	#return list of arches
	return jsonpickle.encode(myDb.get_arches());

@route('/arch', method='PUT')
def put_arch():
	# Add a new arch. TODO: TESTME
	id = request.forms.get('id')
	name = request.forms.get('name')

	if id and name:
		myDb.put_arch(id,name)
	else:
		response.status = "400 - Required fields missing."
	return

@route('/status', method='GET')
def get_statuses():
	response.content_type = "application/json"
	#return list of statuses
	return jsonpickle.encode(myDb.get_statuses());

@route('/status', method='PUT')
def put_status():
	# Add a new status. TODO: TESTME
	id = request.forms.get('id')
	name = request.forms.get('name')

	if id and name:
		myDb.put_status(id,name)
	else:
		response.status = "400 - Required fields missing."
	return

@route('/dist', method='GET')
def get_dists():
	response.content_type = "application/json"
	#return list of distributions
	return jsonpickle.encode(myDb.get_dists());

@route('/dist', method='PUT')
def put_dist():
	# Add a new dist. TODO: TESTME
	id = request.forms.get('id')
	name = request.forms.get('name')

	if id and name:
		myDb.put_dist(id,name)
	else:
		response.status = "400 - Required fields missing."
	return

@route('/format', method='GET')
def get_formats():
	response.content_type = "application/json"
	#return list of package formats
	return jsonpickle.encode(myDb.get_formats());

@route('/format', method='PUT')
def put_format():
	# Add a new format. TODO: TESTME
	id = request.forms.get('id')
	name = request.forms.get('name')

	if id and name:
		myDb.put_format(id,name)
	else:
		response.status = "400 - Required fields missing."
	return

@route('/suite', method='GET')
def get_suites():
	response.content_type = "application/json"
	#return list of suites
	return jsonpickle.encode(myDb.get_suites());

@route('/suite', method='PUT')
def put_suite():
	# Add a new suite. TODO: TESTME
	id = request.forms.get('id')
	name = request.forms.get('name')

	if id and name:
		myDb.put_suite(id,name)
	else:
		response.status = "400 - Required fields missing."
	return
