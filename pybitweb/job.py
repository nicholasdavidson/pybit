#!/usr/bin/python

#       pybit-web
#       Copyright 2012:
#
#		Nick Davidson <nickd@toby-churchill.com>,
#		Simon Haswell <simonh@toby-churchill.com>,
#		Neil Williams <neilw@toby-churchill.com>,
#		James Bennet <github@james-bennet.com / James.Bennet@toby-churchill.com>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

from bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect,request
import jsonpickle
from db import Database,myDb
import job
from controller import Controller,buildController
from pybit.models import Transport,JobHistory

#NEW: proxy to class method controller.add
@route('/job/vcshook', method='POST')
@route('/job/vcshook', method='PUT')
def vcs_hook():
	try:
			response.status = "200 - Version control poke recieved"
			uri = request.forms.get('uri')
			method = request.forms.get('method')
			dist = request.forms.get('distribution')
			vcs_id = request.forms.get('vcs_id')
			architectures = request.forms.get('architecture_list')
			version = request.forms.get('package_version')
			package_name = request.forms.get('package')
			suite = request.forms.get('suite')
			pkg_format = request.forms.get('format')

			if not uri and not method and not dist and not vcs_id and not architectures and not version and not package_name and not suite and not pkg_format :
				response.status = "400 - Required fields missing."
				return None
			else :
				print "RECEIVED BUILD REQUEST FOR", package_name, version, suite, architectures
				buildController.process_job(dist, architectures, version, package_name, suite, pkg_format, Transport(None, method, uri, vcs_id))
				return
	except Exception as e:
		raise Exception('Exception encountered in vcs_hook: ' + str(e))
		response.status = "500 - Exception encountered in vcs_hook"
		return None

@route('/job', method='GET')
def get_jobs():
	try:
		response.content_type = "application/json"
		#return list of ALL jobs
		return jsonpickle.encode(myDb.get_jobs())
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

#NEW: Have controller cancel all jobs.
@route('/job', method='DELETE')
def cancel_jobs():
	try:
		response.status = "202 - CANCEL ALL request recieved"
		buildController.cancel_all_builds()
		return
	except Exception as e:
		raise Exception('Exception encountered: ' + str(e))
		return None

#NEW: Have controller cancel a specific job.
@route('/job/<jobid:int>/cancel', method='GET')
def cancel_job(jobid):
	try:
		response.status = "202 - CANCEL JOB request recieved"
		buildController.cancel_package_instance(jobid)
		return
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
	job_client = None
	if hasattr(request.forms, 'client') :
		job_client = request.forms.client
	if job_status:
		job = myDb.get_job(jobid)
		if job is not None:
			print "Setting ", job.id, " to ", job_status
			myDb.put_job_status(job.id, job_status, job_client)
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
		# Add a new job. Pokes simons controller code with the correct values for uri, method, vcs_id etc...
		packageinstance_id = request.forms.get('packageinstance_id')
		method = request.forms.get('method')
		vcs_id = request.forms.get('vcs_id')
		uri = request.forms.get('uri')

		if  packageinstance_id and method and vcs_id and uri:
			packageinstance = myDb.get_packageinstance_id(packageinstance_id)
			package_version = packageinstance.package.version
			package_name = packageinstance.package.name
			arch =  packageinstance.arch.name # TODO: parse list
			dist = packageinstance.distribution.name
			suite = packageinstance.suite.name
			pkg_format = packageinstance.format.name

			print ("Calling Controller.process_job(" + uri + "," + method + "," + dist + "," + vcs_id  + "," + arch + "," + package_version + "," + package_name  + "," + suite + "," + pkg_format + ")")

			# Pass to controller to queue up
			transport = Transport(None, method, uri, vcs_id)
			buildController.process_job(dist, arch, package_version, package_name, suite, pkg_format, transport)
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

@route('/job/<jobid:int>/delete', method='GET')
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
		# Return status history for specified job ID
		res = myDb.get_job_statuses(jobid)

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
