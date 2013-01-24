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

from pybitweb.bottle import response
from amqplib import client_0_8 as amqp
import jsonpickle
import os
import pybit
from pybit.models import BuildRequest, CancelRequest, JobHistory

class Controller(object):

	def get_amqp_channel(self):
		chan = None
		try:
			conn = amqp.Connection(host=self.settings['controller']['rabbit_url'],
				 userid=self.settings['controller']['rabbit_userid'],
				 password=self.settings['controller']['rabbit_password'],
				 virtual_host=self.settings['controller']['rabbit_virtual_host'],
				 insist=self.settings['controller']['rabbit_insist'])
			try:
				chan = conn.channel()
				chan.exchange_declare(exchange=pybit.exchange_name,
					type="direct",
					durable=True,
					auto_delete=False)
			except amqp.AMQPChannelException:
				pass
		except amqp.AMQPConnectionException:
			pass
		return chan

	def __init__(self, settings, db):
		print "DEBUG: Controller constructor called."
		self.db = db
		self.settings = settings

	def process_job(self, dist, architectures, version, name, suite, pkg_format, transport, commands = None) :
		try:
			# Look at blacklist, dont build excluded package names
			if self.db.check_blacklist("name",name):
				return False
			# Look at blacklist, dont build packages from SVN paths which match the blacklist rule.
			if self.db.check_blacklist("vcs_uri",transport.uri):
				return False
		except Exception as e:
			print "Exception checking blacklist " + str(e)
			return False

		try:
			build_arches = self.process_achitectures(architectures, suite)
			if (len(build_arches) == 0):
				response.status = "404 - no build architectures for this suite."
				return
		except Exception as e:
			raise Exception('Error parsing arch information: ' + str(e))
			response.status = "500 - Error parsing arch information"
			return

		try:
			current_package = self.process_package(name, version)
			if not current_package.id :
				return
			current_suite = self.db.get_suite_byname(suite)[0]
			current_dist = self.db.get_dist_byname(dist)[0]
			current_format = self.db.get_format_byname(pkg_format)[0]
			master = True
			#for arch in supported_arches:
			chan = self.get_amqp_channel()
			for arch in build_arches:
				current_arch = self.db.get_arch_byname(arch)[0]
				current_packageinstance = self.process_packageinstance(current_arch, current_package, current_dist, current_format, current_suite, master)
				if current_packageinstance.id :
					new_job = self.db.put_job(current_packageinstance,None)
					print "CREATED NEW JOB ID", new_job.id
					if new_job.id :
						self.cancel_superceded_jobs(new_job)
						build_req = jsonpickle.encode(BuildRequest(new_job,transport,
							"%s:%s" % (self.settings['web']['hostname'], self.settings['web']['port']),commands))
						msg = amqp.Message(build_req)
						msg.properties["delivery_mode"] = 2
						routing_key = pybit.get_build_route_name(new_job.packageinstance.distribution.name,
												new_job.packageinstance.arch.name,
												new_job.packageinstance.suite.name,
												new_job.packageinstance.format.name)
						build_queue = pybit.get_build_queue_name(new_job.packageinstance.distribution.name,
												new_job.packageinstance.arch.name,
												new_job.packageinstance.suite.name,
												new_job.packageinstance.format.name)
						self.add_message_queue(build_queue, routing_key, chan)

						if chan.basic_publish(msg,exchange=pybit.exchange_name,routing_key=routing_key,mandatory=True) :
							#print "\n____________SENDING", build_req, "____________TO____________", routing_key
							print "SENDING BUILD REQUEST FOR JOB ID", new_job.id, new_job.packageinstance.package.name, new_job.packageinstance.package.version, new_job.packageinstance.distribution.name, new_job.packageinstance.arch.name, new_job.packageinstance.suite.name, new_job.packageinstance.format.name
						else :
							print "UNABLE TO ROUTE BUILD REQUEST TO", routing_key
					else :
						print "FAILED TO ADD JOB"
						response.status = "404 - failed to add job."
					master = False
				else :
					print "PACKAGE INSTANCE ERROR"
					response.status = "404 - failed to add/retrieve package instance."
		except Exception as e:
			raise Exception('Error submitting job: ' + str(e))
			response.status = "500 - Error submitting job"
			return
		return

	def add_message_queue(self, queue, routing_key, chan):
		print "CREATING", chan.queue_declare(queue=queue, durable=True,
										exclusive=False, auto_delete=False)
		print "BINDING", queue, routing_key, chan.queue_bind(queue=queue,
										exchange=pybit.exchange_name, routing_key=routing_key)
		return

	def process_achitectures(self, requested_arches, suite) :
#		print "REQUESTED ARCHITECTURES:", requested_arches
		arches_to_build = list()
		supported_arches = self.db.get_supported_architectures(suite)
		if (len(supported_arches) == 0):
			response.status = "404 - no build architectures for this suite."
		else :
#			print "SUPPORTED ARCHITECTURES:", supported_arches
			if ("all" in requested_arches) and ("any" not in requested_arches) :
				# this is an arch-all request so we only need to build for the first supported arch
				arches_to_build.append(supported_arches[0])
				print "ARCH-ALL REQUEST, ONLY NEED TO BUILD FOR FIRST SUPPORTED ARCH...", arches_to_build
			elif ("any" in requested_arches) :
				# build for all supported arches
				arches_to_build = supported_arches
				print "ARCH-ALL-ANY REQUEST, BUILDING FOR ALL SUPPORTED ARCHES...", arches_to_build
			else :
				for arch in supported_arches :
					if arch in requested_arches :
						arches_to_build.append(arch)
				print "ARCHES TO BUILD:", arches_to_build
		return arches_to_build

	def process_package(self, name, version) :
		# retrieve existing package or try to add a new one
		package = None
		matching_package_versions = self.db.get_package_byvalues(name,version)
		if len(matching_package_versions) > 0 :
			package = matching_package_versions[0]
			if package.id :
				print "MATCHING PACKAGE FOUND (", package.id, package.name, package.version, ")"
		else :
			# add new package to db
			package = self.db.put_package(version,name)
			if package.id :
				print "ADDED NEW PACKAGE (", package.id, package.name, package.version, ")"
		return package

	def process_packageinstance(self, arch, package, dist, pkg_format, suite, master) :
		# check & retrieve existing package or try to add a new one
		packageinstance = None
		if self.db.check_specific_packageinstance_exists(arch, package, dist, pkg_format, suite) :
			# retrieve existing package instance from db
			packageinstance = self.db.get_packageinstance_byvalues(package, arch, suite, dist, pkg_format)[0]
			if packageinstance.id :
				print "MATCHING PACKAGE INSTANCE FOUND (", packageinstance.id, ")"
				# Temporarily disable master update for Issue #84, this should not be default behaviour.
#				if packageinstance.master != master :
#					print "UPDATING PACKAGE INSTANCE MASTER FLAG (", master, ")"
#					self.db.update_packageinstance_masterflag(packageinstance.id,master)
#					packageinstance.master = master
		else :
			# add new package instance to db
			packageinstance = self.db.put_packageinstance(package, arch, suite, dist, pkg_format, master)
			if packageinstance.id :
				print "ADDED NEW PACKAGE INSTANCE (", packageinstance.id, ")"
		return packageinstance

	def process_cancel(self, job, chan):
		job_status_history = self.db.get_job_statuses(job.id)
		last_status = job_status_history[-1].status
		build_client = job_status_history[-1].buildclient
		if (len(job_status_history) > 0) and (last_status == "Building") and (build_client != None) :
			cancel_req = jsonpickle.encode(CancelRequest(job,"%s:%s" % (self.settings['web']['hostname'], self.settings['web']['port'])))
			msg = amqp.Message(cancel_req)
			msg.properties["delivery_mode"] = 2
			print "UNFINISHED JOB ID", job.id, "STATUS:", last_status, "SENDING CANCEL REQUEST TO", build_client
			chan.basic_publish(msg,exchange=pybit.exchange_name,routing_key=build_client)
		else :
			print "UNFINISHED JOB ID", job.id, "STATUS:", last_status, "UPDATE STATUS TO 'Cancelled'"
			self.db.put_job_status(job.id, "Cancelled", build_client)
		return

	def cancel_superceded_jobs(self, new_job) :
		# check for unfinished jobs that might be cancellable
		packageinstance = new_job.packageinstance
		unfinished_jobs_list = self.db.get_unfinished_jobs()
		#print "UNFINISHED JOB LIST", unfinished_jobs_list
		chan = self.get_amqp_channel()
		for unfinished_job in unfinished_jobs_list:
			unfinished_job_package_name = unfinished_job.packageinstance.package.name
			if unfinished_job_package_name == packageinstance.package.name :
				if new_job.id != unfinished_job.id :
					unfinished_job_package_version = unfinished_job.packageinstance.package.version
					command = "dpkg --compare-versions %s '<<' %s" % (packageinstance.package.version, unfinished_job_package_version)
					if (unfinished_job_package_version == packageinstance.package.version) or (os.system (command)) :
						unfinished_job_dist_id = unfinished_job.packageinstance.distribution.id
						unfinished_job_arch_id = unfinished_job.packageinstance.arch.id
						unfinished_job_suite_id = unfinished_job.packageinstance.suite.id
						if (unfinished_job_dist_id == packageinstance.distribution.id) and (unfinished_job_arch_id == packageinstance.arch.id) and (unfinished_job_suite_id == packageinstance.suite.id) :
							self.process_cancel(unfinished_job, chan)
#						else :
#							print "IGNORING UNFINISHED JOB", unfinished_job.id, unfinished_job_package_name, unfinished_job_package_version, "(dist/arch/suite differs)"
#					else :
#						print "IGNORING UNFINISHED JOB", unfinished_job.id, unfinished_job_package_name, unfinished_job_package_version, "(version differs)"
#				else :
#					print "IGNORING NEW JOB", unfinished_job.id
#			else :
#				print "IGNORING UNFINISHED JOB", unfinished_job.id, unfinished_job_package_name
		return

	def cancel_all_builds(self):
		print "DEBUG: Cancelling all builds!"
		# cancels all packages/jobs
		unfinished_jobs_list = self.db.get_unfinished_jobs()
		for unfinished_job in unfinished_jobs_list:
			chan = self.get_amqp_channel()
			self.process_cancel(unfinished_job, chan)
		return

	def cancel_package(self, package_id):
		# cancels all instances of a package
		package = self.db.get_package_id(package_id)
		if not package.id :
			response.status = "404 - no package matching package_id"
		else :
			unfinished_jobs_list = self.db.get_unfinished_jobs()
			for unfinished_job in unfinished_jobs_list:
				if (unfinished_job.packageinstance.package.name == package.name) and (unfinished_job.packageinstance.package.version == package.version):
					chan = self.get_amqp_channel()
					self.process_cancel(unfinished_job, chan)
		return

	def cancel_package_instance(self,job_id): #FIXME: rename...
		# cancels a specific job/package instance
		try:
			if not job_id :
				response.status = "400 - Required fields missing."
				return
			else :
				job_to_cancel = self.db.get_job(job_id)
				if not job_to_cancel :
					response.status = "404 - no job matching id"
				else :
					chan = self.get_amqp_channel()
					self.process_cancel(job_to_cancel, chan)
		except Exception as e:
			raise Exception('Error parsing job information: ' + str(e))
			response.status = "500 - Error parsing job information"
			return
		return


	def buildd_command_queue_exists(self, build_client):
		try:
			print "Checking if queue exists: " + build_client
			chan = self.get_amqp_channel()
			chan.queue_declare(queue=build_client, passive=True, durable=True,
								exclusive=False, auto_delete=False,)
			return False
		except amqp.AMQPChannelException as e:
			if e.amqp_reply_code == 405:
				print "405 from buildd_command_queue_exists. Returning True."
				return True # Locked i.e. exists
			elif e.amqp_reply_code == 404:
				print "404 from buildd_command_queue_exists. Returning False."
				return False # doesnt exist
			else:
				return False
		except Exception as e:
			print "Error in buildd_command_queue_exists. Returning False." + str(e)
			return False;  # Error
