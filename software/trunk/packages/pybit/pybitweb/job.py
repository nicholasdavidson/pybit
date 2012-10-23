#!/usr/bin/python

from bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect,request
import jsonpickle
from db import Database
import job

myDb = Database()

@route('/job', method='GET')
def get_jobs():
	try:
		response.content_type = "application/json"
		#return list of ALL jobs"
		return jsonpickle.encode(myDb.get_jobs());
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/job/status', method='GET')
def get_jobstatuses():
	try:
		response.content_type = "application/json"
		#return list of UNFINISHED jobs"
		res = myDb.get_unfinished_jobs()
		return jsonpickle.encode(res)
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/job/<jobid:int>', method='PUT')
@route('/job/<jobid:int>', method='POST')
def update_job_status(jobid):
	job_status = request.forms.status
	if job_status:
		job = myDb.get_job(jobid)
		if job is not None:
			print "Setting ", job.id, " to ", job_status
			myDb.put_job_status(job.id, job_status)
		else:
			response.status = "404 - No job found with this ID."
			return
	else:
		response.status = "400 - Required fields missing."
		return

@route('/job/status/<status>', method='GET')
def get_jobs_bystatus(status):
	try:
		response.content_type = "application/json"
		#return list of UNFINISHED jobs"
		res = myDb.get_jobs_by_status(status)
		return jsonpickle.encode(res)
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

@route('/job', method='POST')
@route('/job', method='PUT')
def put_job():
	try:
		# Add a new job. TODO: Make this poke simons controller code with the correct values for uri, method, vcs_id, architecture_list
		packageinstance_id = request.forms.get('packageinstance_id')
		buildclient_id =  request.forms.get('buildclient_id')

		if  packageinstance_id and buildclient_id:
			# original
			packageinstance = myDb.get_packageinstance_id(packageinstance_id)
			package_version = packageinstance.package.version
			package_name = packageinstance.package.name
			buildclient = myDb.get_buildd_id(buildclient_id)

			dist = packageinstance.distribution.name
			suite = packageinstance.suite.name
			format = packageinstance.format.name

			print "TODO: call Controller.add(uri,method," , dist, ",vcs_id,architecture_list," + package_version + "," + package_name + "," + suite + "," + format

			myDb.put_job(packageinstance,buildclient)
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
		if res:
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
		# TODO: CODEME! - SHOW STATUS HISTORY
		res = myDb.get_job_status(jobid)
		response.status = "501 - ERROR: Not coded yet."
		return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None
