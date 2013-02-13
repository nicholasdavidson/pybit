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
import logging
import sys
from db import Database
import bottle_basic_auth
from bottle_basic_auth import requires_auth
from controller import Controller
from pybit.models import Transport,JobHistory
import psycopg2.errorcodes

#NEW: proxy to class method controller.add
def get_job_app(settings, db, controller) :
	app = Bottle()
	app.config={'settings':settings, 'db':db, 'controller': controller}

	app.log = logging.getLogger( "web" )
	if (('debug' in settings['web']) and ( settings['web']['debug'])) :
		app.log.setLevel( logging.DEBUG )

	@app.route('/vcshook', method='POST')
	@app.route('/vcshook', method='PUT')
	@requires_auth
	def vcs_hook():
		try:
				response.status = "200 - Version control poke received"
				uri = request.forms.get('uri')
				method = request.forms.get('method')
				dist = request.forms.get('distribution')
				vcs_id = request.forms.get('vcs_id')
				architectures = request.forms.get('architecture_list')
				version = request.forms.get('package_version')
				package_name = request.forms.get('package')
				suite = request.forms.get('suite')
				pkg_format = request.forms.get('format')

				if not uri and not method and not dist and not architectures and not version and not package_name and not suite and not pkg_format :
					response.status = "400 - Required fields missing."
					return None
				else :
					app.log.debug("RECEIVED BUILD REQUEST FOR %s, %s, %s, %s", package_name, version, suite, architectures)
					# NOTE:VCS Hook does not send build_environment.
					if app.config['controller'].process_job(dist, architectures, version, package_name, suite, pkg_format, Transport(None, method, uri, vcs_id),None):
						return
					else:
						return False
		except Exception as e:
			raise Exception('Exception encountered in vcs_hook: ' + str(e))
			response.status = "500 - Exception encountered in vcs_hook"
			return None

	@app.route('/', method='GET')
	@app.route('/page/<page:int>', method='GET')
	def get_jobs(page = None):
		try:
			response.content_type = "application/json"
			#return list of ALL jobs
			if page:
				return jsonpickle.encode(app.config['db'].get_jobs(page))
			else:
				return jsonpickle.encode(app.config['db'].get_jobs())
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	#NEW: Have controller cancel all jobs.
	@app.route('/cancelall', method='GET')
	@app.route('/', method='DELETE')
	@requires_auth
	def cancel_jobs():
		try:
			response.status = "202 - CANCEL ALL request received"
			app.config['controller'].cancel_all_builds()
			return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	#NEW: Have controller cancel a specific job.
	@app.route('/<jobid:int>/cancel', method='GET')
	@requires_auth
	def cancel_job(jobid):
		try:
			response.status = "202 - CANCEL JOB request received"
			app.config['controller'].cancel_package_instance(jobid)
			return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	@app.route('/status', method='GET')
	def get_jobstatuses():
		try:
			response.content_type = "application/json"
			#return list of UNFINISHED jobs"
			res = app.config['db'].get_unfinished_jobs()
			return jsonpickle.encode(res)
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	@app.route('/<jobid:int>', method='PUT')
	@app.route('/<jobid:int>', method='POST')
	@requires_auth
	def update_job_status(jobid):
		job_status = request.forms.status
		job_client = None
		if hasattr(request.forms, 'client') :
			job_client = request.forms.client
		if job_status:
			job = app.config['db'].get_job(jobid)
			if job is not None:
				app.log.debug("Setting job:%i to %s", job.id, job_status)
				app.config['db'].put_job_status(job.id, job_status, job_client)
			else:
				response.status = "404 - No job found with this ID."
				return
		else:
			response.status = "400 - Required fields missing."
			return

	@app.route('/status/<status>', method='GET')
	def get_jobs_bystatus(status):
		try:
			response.content_type = "application/json"
			#return list of UNFINISHED jobs"
			res = app.config['db'].get_jobs_by_status(status)
			return jsonpickle.encode(res)
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	@app.route('/<jobid:int>/retry', method='GET')
	@requires_auth
	def retry_job(jobid):
		#  TODO: Improve this.
		# This will retry a job, using the same stashed Transport data, from the buildrequest table.

		app.log.debug("Retry job request recieved for job id:%i", jobid)

		job = app.config['db'].get_job(jobid)
		transport = app.config['db'].get_jobTransportDetails(jobid)

		package_version = job.packageinstance.get_package_version()
		package_name = job.packageinstance.get_package_name()
		arch =  job.packageinstance.get_arch_name() # TODO: parse list
		dist = job.packageinstance.get_distribution_name()
		suite = job.packageinstance.get_suite_name()
		pkg_format = job.packageinstance.get_format_name()
		build_environment = job.packageinstance.get_buildenv_name()

		method = transport.method
		vcs_id = transport.vcs_id
		uri = transport.uri

		# Pass to controller to queue up - Pass build_environment if any.
		if app.config['controller'].process_job(dist,arch,package_version,package_name,suite,pkg_format,transport,build_environment):
			app.log.debug("Retry job processed OK!")
			return
		else:
			app.log.debug("Error retrying job!")
			return False


	@app.route('/', method='POST')
	@app.route('/', method='PUT')
	@requires_auth
	def put_job():
		try:
			# Add a new job. Pokes simons controller code with the correct values for uri, method, vcs_id etc...
			packageinstance_id = request.forms.get('packageinstance_id')
			method = request.forms.get('method')
			vcs_id = request.forms.get('vcs_id')
			uri = request.forms.get('uri')

			if  packageinstance_id and method and uri:
				packageinstance = app.config['db'].get_packageinstance_id(packageinstance_id)
				package_version = packageinstance.get_package_version()
				package_name = packageinstance.get_package_name()
				arch =  packageinstance.get_arch_name() # TODO: parse list
				dist = packageinstance.get_distribution_name()
				suite = packageinstance.get_suite_name()
				pkg_format = packageinstance.get_format_name()
				build_environment = packageinstance.get_buildenv_name()

				# Pass to controller to queue up - Pass build_environment if any.
				transport = Transport(None, method, uri, vcs_id)
				if app.config['controller'].process_job(dist,arch,package_version,package_name,suite,pkg_format,transport,build_environment):
					return
				else:
					return False
			else:
				response.status = "400 - Required fields missing."
			return
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	@app.route('/<jobid:int>', method='GET')
	def get_jobid(jobid):
		try:
			# Return details for specified job ID
			res = app.config['db'].get_job(jobid)

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

	@app.route('/<jobid:int>/delete', method='GET')
	@app.route('/<jobid:int>', method='DELETE')
	@requires_auth
	def del_jobid(jobid):
		try:
			# Deletes a specific job
			retval = app.config['db'].delete_job(jobid)

			if(retval == True):
				response.status = "200 DELETE OK"
			elif(retval == False):
				response.status = "404 Cannot DELETE"
			elif(retval == "23503"):
				response.status = "409 " + str(errorcodes.lookup(retval))
			else:
				response.status = "500 " + str(errorcodes.lookup(retval))

			return response.status
		except Exception as e:
			raise Exception('Exception encountered: ' + str(e))
			return None

	@app.route('/<jobid:int>/status', method='GET')
	def get_jobstatus(jobid):
		try:
			# Return status history for specified job ID
			res = app.config['db'].get_job_statuses(jobid)

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
	return app
