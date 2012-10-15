#!/usr/bin/python

from pybitweb.bottle import Bottle,response,error,request
from amqplib import client_0_8 as amqp
import jsonpickle
import os.path

import db
from models import transport, packageinstance, job, deb_package
# example CURL command....
# /usr/bin/curl -X POST http://localhost:8080/add --data "uri=http://svn.tcl.office/svn/lwdev&directory=software/branches/software_release_chickpea/packages/appbarwidget&method=svn&distribution=Debian&vcs_id=20961&architecture_list=all,any&package_version=0.6.33chickpea47&package=appbarwidget&suite=chickpea&format=deb"

# PyBit setup variables - package content
queue_name = "rabbit"
report_name = "controller"
listening_name = "buildd"
dput_cfg = "/etc/pybit/client/dput.cf"

class controller:

	def __init__(self, jobDb):
		self.job_db = jobDb
		self.conn = amqp.Connection(host="localhost:5672", userid="guest", password="guest", virtual_host="/", insist=False)
		self.chan = self.conn.channel()
		print "controller init"

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

			trans = transport(None, method, uri, vcs_id)

			if not uri and method and dist and vcs_id and architectures and version and package_name and suite and format :
				response.status = "400 - Required fields missing."
				return
			else :
				print package_name, version, suite, architectures
		except Exception as e:
			raise Exception('Error parsing job information: ' + str(e))
			response.status = "500 - Error parsing job information"
			return None

		try:
			supported_arches = self.job_db.supportedArchitectures(suite)
			print "SUPPORTED ARCHITECTURES:", supported_arches

			if (len(supported_arches) == 0):
				response.status = "404 - no supported architectures for this suite."
				return
		except Exception as e:
			raise Exception('Error parsing arch information: ' + str(e))
			response.status = "500 - Error parsing arch information"
			return None

		try:
			if (architectures and len(architectures) == 1 and architectures[0] == "all"):
				# TODO: check_specific_packageinstance_exists
				new_packageinstance = packageinstance(suite, package_name, version, supported_arches[0], format, dist, trans)
			else :
				current_package = None
				matching_package_versions = self.job_db.get_package_byvalues(package_name,version)
				if len(matching_package_versions) < 0 :
					print "FOUND", len(matching_package_versions)
					current_package = matching_package_versions[0]
				else :
					print "NO MATCHING PACKAGE FOUND"
					# add new package to db
					current_package = self.job_db.put_package(version,package_name)
					if not current_package.id :
						#TODO: throw error???
						print "FAILED TO ADD PACKAGE:", package_name
						response.status = "404 - failed to add package."
						return
					else :
						print "ADDED PACKAGE", current_package.id
				current_suite_id = self.job_db.get_suite_byname(suite)[0].id
				current_dist_id = self.job_db.get_dist_byname(dist)[0].id
				current_format_id = self.job_db.get_format_byname(format)[0].id
				for arch in supported_arches:
					if not self.job_db.check_specific_packageinstance_exists(arch, dist, format, package_name, version, suite) :
						current_arch_id = self.job_db.get_arch_byname(arch)[0].id
						# add package instance to db
						new_packageinstance = self.job_db.put_packageinstance(current_package.id,current_arch_id,current_suite_id,current_dist_id,current_format_id,False)
						if new_packageinstance.id :
							# TODO: check if database contains a package where status = building, version < package_version, suite = suite
							new_job = self.job_db.put_job(new_packageinstance.id, None)
							if new_job.id :
								print "ADDED Job:", new_job.id, "PackageInstance:", new_packageinstance.id, "for", arch
								#TODO: tidy in model so deb_package inherits from package & transport
								jobToSend = deb_package(current_package.name,current_package.version,format,dist,trans.method,trans.uri,trans.vcs_id,arch,suite)
								pickled = jsonpickle.encode(jobToSend)
								print "Sending " ,pickled
								msg = amqp.Message(pickled)
								msg.properties["delivery_mode"] = 2
								self.chan.basic_publish(msg,exchange="i386",routing_key="buildd")
							else :
								print "FAILED TO ADD JOB"
								response.status = "404 - failed to add job."
						else :
							print "FAILED TO ADD PACKAGE INSTANCE!"
							response.status = "404 - failed to add package instance."
				# cancel any job older jobs matching this package on queue
		except Exception as e:
			raise Exception('Error submitting job: ' + str(e))
			response.status = "500 - Error submitting job"
			return None
		return

	def cancelAllBuilds(self):
		return

	def cancelPackage(self):
		return

	def cancelPackageInstance(self):
		return
