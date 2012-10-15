#!/usr/bin/python

from bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect,request
import jsonpickle
from db import db
from models import arch,dist,format,status,suite
myDb = db()

@route('/arch', method='GET')
def get_arch():
	try:
		#return list of arches
		arches = myDb.get_arches()
		encoded = jsonpickle.encode(arches)
		response.content_type = "application/json"
		return encoded
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/arch/<id:int>', method='GET')
def get_arch_id(id):
	try:
		# Returns all information about a specific arch
		res = myDb.get_arch_id(id)

		# check results returned
		if len(res) > 0:
			encoded = jsonpickle.encode(res)
			response.content_type = "application/json"
			return encoded
		else:
			response.status = "404 - No arch found with this ID."
			return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/arch', method='POST')
@route('/arch', method='PUT')
def put_arch():
	try:
		# Add a new arch. TODO: TESTME
		name = request.forms.get('name')

		if name:
			myDb.put_arch(name)
		else:
			response.status = "400 - Required fields missing."
		return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/status', method='GET')
def get_statuses():
	try:
		#return list of statuses
		statuses = myDb.get_statuses()
		encoded = jsonpickle.encode(statuses)
		response.content_type = "application/json"
		return encoded
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/status/<id:int>', method='GET')
def get_status_id(id):
	try:
		# Returns all information about a specific status
		res = myDb.get_status_id(id)

		# check results returned
		if len(res) > 0:
			encoded = jsonpickle.encode(res)
			response.content_type = "application/json"
			return encoded
		else:
			response.status = "404 - No status found with this ID."
			return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/status', method='POST')
@route('/status', method='PUT')
def put_status():
	try:
		# Add a new status. TODO: TESTME
		name = request.forms.get('name')

		if name:
			myDb.put_status(name)
		else:
			response.status = "400 - Required fields missing."
		return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/dist', method='GET')
def get_dists():
	try:
		#return list of distributions
		dists = myDb.get_dists()
		encoded = jsonpickle.encode(dists)
		response.content_type = "application/json"
		return encoded
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/dist/<id:int>', method='GET')
def get_dist_id(id):
	try:
		# Returns all information about a specific dist
		res = myDb.get_dist_id(id)

		# check results returned
		if len(res) > 0:
			encoded = jsonpickle.encode(res)
			response.content_type = "application/json"
			return encoded
		else:
			response.status = "404 - No dist found with this ID."
			return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/dist', method='POST')
@route('/dist', method='PUT')
def put_dist():
	try:
		# Add a new dist. TODO: TESTME
		name = request.forms.get('name')

		if name:
			myDb.put_dist(name)
		else:
			response.status = "400 - Required fields missing."
		return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/format', method='GET')
def get_formats():
	try:
		#return list of package formats
		formats = myDb.get_formats()
		encoded = jsonpickle.encode(formats)
		response.content_type = "application/json"
		return encoded
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/format/<id:int>', method='GET')
def get_format_id(id):
	try:
		# Returns all information about a specific format
		res = myDb.get_format_id(id)

		# check results returned
		if len(res) > 0:
			encoded = jsonpickle.encode(res)
			response.content_type = "application/json"
			return encoded
		else:
			response.status = "404 - No format found with this ID."
			return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/format', method='POST')
@route('/format', method='PUT')
def put_format():
	try:
		# Add a new format. TODO: TESTME
		name = request.forms.get('name')

		if name:
			myDb.put_format(name)
		else:
			response.status = "400 - Required fields missing."
		return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/suite', method='GET')
def get_suites():
	try:
		#return list of suites
		suites = myDb.get_suites()
		encoded = jsonpickle.encode(suites)
		response.content_type = "application/json"
		return encoded
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/suite/<id:int>', method='GET')
def get_suite_id(id):
	try:
		# Returns all information about a specific suite
		res = myDb.get_suite_id(id)

		# check results returned
		if len(res) > 0:
			encoded = jsonpickle.encode(res)
			response.content_type = "application/json"
			return encoded
		else:
			response.status = "404 - No suite found with this ID."
			return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/suite', method='POST')
@route('/suite', method='PUT')
def put_suite():
	try:
		# Add a new suite. TODO: TESTME
		name = request.forms.get('name')

		if name:
			myDb.put_suite(name)
		else:
			response.status = "400 - Required fields missing."
		return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None
