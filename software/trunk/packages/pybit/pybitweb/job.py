#!/usr/bin/python

from bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect,request
import jsonpickle
from db import db
import job

myDb = db()

@route('/job', method='GET')
def get_jobs():
	try:
		response.content_type = "application/json"
		#return list of jobs"
		return jsonpickle.encode(myDb.get_jobs());
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/job', method='POST')
@route('/job', method='PUT')
def put_job():
	try:
		# Add a new job. TODO: TESTME
		packageinstance_id = request.forms.get('packageinstance_id')
		buildclient_id =  request.forms.get('buildclient_id')

		if  packageinstance_id and buildclient_id:
			myDb.put_job(packageinstance_id,buildclient_id)
		else:
			response.status = "400 - Required fields missing."
		return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/job/<jobid:int>', method='GET')
def get_jobid(jobid):
	try:
		# Return details for specified job ID
		res = myDb.get_job(jobid)

		# check results returned
		if len(res) > 0:
			encoded = jsonpickle.encode(res)
			response.content_type = "application/json"
			return encoded
		else:
			response.status = "404 - No job found with this ID."
			return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/job/<jobid:int>', method='DELETE')
def del_jobid(jobid):
	try:
		# Deletes a specific job
		# TODO: validation,security
		response.status = "202 - DELETE request recieved"
		myDb.delete_job(jobid)
		return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/job/<jobid:int>/status', method='GET')
def get_jobstatus(jobid):
	try:
		# Return status for specified job ID
		res = myDb.get_job_status(jobid)

		# check results returned
		if len(res) > 0:
			encoded = jsonpickle.encode(res)
			response.content_type = "application/json"
			return encoded
		else:
			response.status = "404 - No statuses found for job with this ID."
			return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None
