#!/usr/bin/python

from bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect
import jsonpickle
from db import db

myDb = db()

@route('/job', method='GET')
def get_jobs():
	response.content_type = "application/json"
	#return list of jobs"
	return jsonpickle.encode(myDb.get_jobs());

@route('/job', method='PUT')
def put_job():
	response.status = "201 - PUT a job."
	#TODO: work in progress
	return

@route('/job/<jobid:int>', method='GET')
def get_jobid(jobid):
	response.content_type = "application/json"
	# Return details for specified job ID
	res = myDb.get_job(jobid)

	# check results returned
	if len(res) > 0:
		return jsonpickle.encode(res)
	else:
		response.status = "404 - No job found with this ID."
		return

@route('/job/<jobid:int>', method='DELETE')
def del_jobid(jobid):
	# TODO: validation,security
	response.status = "202 - DELETE request recieved"
	myDb.delete_job(jobid)
	return

@route('/job/<jobid:int>/status', method='GET')
def get_jobstatus(jobid):
	response.content_type = "application/json"
	# Return status for specified job ID
	res = myDb.get_job_status(jobid)

	# check results returned
	if len(res) > 0:
		return jsonpickle.encode(res)
	else:
		response.status = "404 - No statuses found for job with this ID."
		return
