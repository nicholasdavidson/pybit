#!/usr/bin/python

from pybitweb.bottle import Bottle,response,error,request
from amqplib import client_0_8 as amqp
import jsonpickle
import os.path
import pybit
from db import Database
from pybit.models import Transport, BuildRequest, CancelRequest

class Controller:

	def __init__(self, db):
		try:
			self.build_db = db
			self.conn = amqp.Connection(host="localhost:5672", userid="guest", password="guest", virtual_host="/", insist=False)
			self.chan = self.conn.channel()
			#declare exchange.
			self.chan.exchange_declare(exchange=pybit.exchange_name, type="direct", durable=True, auto_delete=False)
			#declare command queue.
			self.chan.queue_declare(queue=pybit.status_queue, durable=True, exclusive=False, auto_delete=False)
			#bind routing from exchange to command queue based on routing key.
			self.chan.queue_bind(queue=pybit.status_queue, exchange=pybit.exchange_name, routing_key=pybit.status_route)
			print "controller init"
		except Exception as e:
			raise Exception('Error creating controller (Maybe we cannot connect to queue?) - ' + str(e))
			return

	def add(self):
		try:
			uri = request.forms.get('uri')
			method = request.forms.get('method')
			dist = request.forms.get('distribution')
			vcs_id = request.forms.get('vcs_id')
			architectures = request.forms.get('architecture_list')
			version = request.forms.get('package_version')
			package_name = request.forms.get('package')
			suite = request.forms.get('suite')
			format = request.forms.get('format')

			trans = Transport(None, method, uri, vcs_id)

			if not uri and not method and not dist and not vcs_id and not architectures and not version and not package_name and not suite and not format :
				response.status = "400 - Required fields missing."
				return
			else :
				print "RECEIVED BUILD REQUEST FOR", package_name, version, suite, architectures
		except Exception as e:
			raise Exception('Error parsing job information: ' + str(e))
			response.status = "500 - Error parsing job information"
			return

		try:
			supported_arches = self.build_db.get_supported_architectures(suite)
			print "SUPPORTED ARCHITECTURES:", supported_arches

			if (len(supported_arches) == 0):
				response.status = "404 - no supported architectures for this suite."
				return
		except Exception as e:
			raise Exception('Error parsing arch information: ' + str(e))
			response.status = "500 - Error parsing arch information"
			return

		try:
			if (architectures and len(architectures) == 1 and architectures[0] == "all"):
				# TODO: check_specific_packageinstance_exists
				new_packageinstance = packageinstance(suite, package_name, version, supported_arches[0], format, dist, trans)
			else :
				current_package = None
				matching_package_versions = self.build_db.get_package_byvalues(package_name,version)
				if len(matching_package_versions) > 0 :
					current_package = matching_package_versions[0]
					print "MATCHING PACKAGE FOUND (", current_package.id, current_package.name, current_package.version, ")"
				else :
					print "NO MATCHING PACKAGE FOUND"
					# add new package to db
					current_package = self.build_db.put_package(version,package_name)
					if not current_package.id :
						#print "FAILED TO ADD PACKAGE:", package_name
						response.status = "404 - failed to add package."
						return
					else :
						print "ADDED NEW PACKAGE (", current_package.id, current_package.name, current_package.version, ")"
				
				current_suite = self.build_db.get_suite_byname(suite)[0]
				current_dist = self.build_db.get_dist_byname(dist)[0]
				current_format = self.build_db.get_format_byname(format)[0]
				
				for arch in supported_arches:
					current_arch = self.build_db.get_arch_byname(arch)[0]
					if not self.build_db.check_specific_packageinstance_exists(current_arch, current_package, current_dist, current_format, current_suite) :
						# add package instance to db
						new_packageinstance = self.build_db.put_packageinstance(current_package, current_arch, current_suite, current_dist, current_format, False)
						if new_packageinstance.id :
							print "CREATED NEW PACKAGE INSTANCE ID", new_packageinstance.id
							new_job = self.build_db.put_job(new_packageinstance,None)
							#print "CREATED NEW JOB ID", new_job.id
							if new_job.id :
								# check for unfinished jobs that might be cancellable
								unfinished_jobs_list = self.build_db.get_unfinished_jobs()
								#print "UNFINISHED JOB LIST", unfinished_jobs_list
								for unfinished_job in unfinished_jobs_list: 
									unfinished_job_package_name = unfinished_job.packageinstance.package.name
									if unfinished_job_package_name == package_name :
										unfinished_job_package_version = unfinished_job.packageinstance.package.version
										command = "dpkg --compare-versions %s '<<' %s" % (version, unfinished_job_package_version)
										if os.system (command) :
											unfinished_job_dist = unfinished_job.packageinstance.distribution.name
											unfinished_job_arch = unfinished_job.packageinstance.arch.name
											unfinished_job_suite = unfinished_job.packageinstance.suite.name
											if (unfinished_job_dist == dist) and (unfinished_job_arch == arch) and (unfinished_job_suite == suite) :
												self.send_cancel_request(unfinished_job)
#											else :
#												print "IGNORING UNFINISHED JOB", unfinished_job_package_name, unfinished_job_package_version, unfinished_job_dist, unfinished_job_arch, unfinished_job_suite
#										else :
#											print "IGNORING UNFINISHED JOB", unfinished_job_package_name, unfinished_job_package_version
#									else :
#										print "IGNORING UNFINISHED JOB", unfinished_job_package_name
								build_req = jsonpickle.encode(BuildRequest(new_job,trans,"localhost:8080"))
								msg = amqp.Message(build_req)
								msg.properties["delivery_mode"] = 2
								routing_key = pybit.get_build_route_name(new_job.packageinstance.distribution.name, new_job.packageinstance.arch.name, new_job.packageinstance.suite.name, new_job.packageinstance.format.name)
								print "SENDING BUILD REQUEST FOR JOB ID", new_job.id, new_job.packageinstance.package.name, new_job.packageinstance.package.version, new_job.packageinstance.distribution.name, new_job.packageinstance.arch.name, new_job.packageinstance.suite.name, new_job.packageinstance.format.name
								#print "\n____________SENDING", build_req, "____________TO____________", routing_key
								self.chan.basic_publish(msg,exchange=pybit.exchange_name,routing_key=routing_key)
							else :
								print "FAILED TO ADD JOB"
								response.status = "404 - failed to add job."
						else :
							print "FAILED TO ADD PACKAGE INSTANCE!"
							response.status = "404 - failed to add package instance."
					else : 
						print "IGNORING REQUEST - PACKAGE INSTANCE ALREADY EXISTS"
						response.status = "404 - ignored request package instance already exists."
		except Exception as e:
			raise Exception('Error submitting job: ' + str(e))
			response.status = "500 - Error submitting job"
			return
		return

	def cancel_all_builds(self):
		unfinished_jobs_list = self.build_db.get_unfinished_jobs()
		for unfinished_job in unfinished_jobs_list: 
			self.send_cancel_request(unfinished_job)
		return

	def cancel_package(self):
		version = request.forms.get('package_version')
		package_name = request.forms.get('package')
		unfinished_jobs_list = self.build_db.get_unfinished_jobs()
		for unfinished_job in unfinished_jobs_list: 
			if (unfinished_job.packageinstance.package.name == package_name) and (unfinished_job.packageinstance.package.version == version):
				self.send_cancel_request(unfinished_job)
		return

	def cancel_package_instance(self):
		try:
			job_id = request.forms.get('job_id')
			if not job_id :
				response.status = "400 - Required fields missing."
				return
			else :
				job_to_cancel = self.build_db.get_job(job_id)
				if not job_to_cancel :
					response.status = "404 - no job matching id"
				else :
					self.send_cancel_request(job_to_cancel)
		except Exception as e:
			raise Exception('Error parsing job information: ' + str(e))
			response.status = "500 - Error parsing job information"
			return
		return

	def send_cancel_request(self, job):
		print "SENDING CANCEL REQUEST FOR JOB ID", job.id, job.packageinstance.package.name, job.packageinstance.package.version, job.packageinstance.distribution.name, job.packageinstance.arch.name, job.packageinstance.suite.name, job.packageinstance.format.name
		cancel_req = jsonpickle.encode(CancelRequest(job,"localhost:8080"))
		msg = amqp.Message(cancel_req)
		msg.properties["delivery_mode"] = 2
		routing_key = pybit.get_build_route_name(job.packageinstance.distribution.name, job.packageinstance.arch.name, job.packageinstance.suite.name, job.packageinstance.format.name)
		#print "\n____________SENDING", cancel_req, "____________TO____________", routing_key
		self.chan.basic_publish(msg,exchange=pybit.exchange_name,routing_key=routing_key)
