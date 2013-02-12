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
import logging
import sys
from pybit.models import BuildRequest, CancelRequest, JobHistory, BuildEnv,\
	BuildEnvSuiteArch, SuiteArch
from jsonpickle import json

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
		self.db = db
		self.settings = settings
		if (('debug' in self.settings['controller']) and ( self.settings['controller']['debug'])) :
				FORMAT = '%(asctime)s %(filename)s:%(lineno)d %(msg)s'
				logging.basicConfig( stream=sys.stderr, level=logging.DEBUG)
				logging.basicConfig( format=FORMAT )
		logging.debug("Controller constructor called.")

	def process_job(self, dist, architectures, version, name, suite, pkg_format, transport, build_environment = None) :
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
			current_package = self.process_package(name, version)
			if not current_package.id :
				return False

			current_suite = self.db.get_suite_byname(suite)[0]
			current_dist = self.db.get_dist_byname(dist)[0]
			current_format = self.db.get_format_byname(pkg_format)[0]

			build_env_suite_arch = self.process_build_environment_architectures(current_suite,architectures,build_environment)

			if len(build_env_suite_arch) == 0:
				logging.warn("INVALID BUILD ENV SUITE ARCH MAPPINGS FOR %s, %s, %s - CHECK YOU HAVE SOME CONFIGURED.", current_suite,architectures,build_environment)
				response.status = "500 - Error submitting job"
				return
			else:
				current_build_env = build_env_suite_arch[0].buildenv
				master_flag = True

			chan = self.get_amqp_channel()
			for build_env_suite_arch in build_env_suite_arch :
				current_arch = build_env_suite_arch.suitearch.arch
				if current_build_env.name != build_env_suite_arch.buildenv.name :
					#first packageinstance for each build environment should have master flag set
					master_flag = True
				current_build_env = build_env_suite_arch.buildenv
				current_packageinstance = self.process_packageinstance(current_build_env, current_arch, current_package, current_dist, current_format, current_suite, master_flag)
				if current_packageinstance.id :
					new_job = self.db.put_job(current_packageinstance,None)
					if (new_job and new_job.id):
#						logging.debug("\nCREATED NEW JOB: %s\n", jsonpickle.encode(new_job))
						self.cancel_superceded_jobs(new_job)
						# NEW STUFF FOR RESUBMITTING JOBS
						build_request_obj = BuildRequest(new_job,transport,
							"%s:%s" % (self.settings['web']['hostname'], self.settings['web']['port']));
						build_req = jsonpickle.encode(build_request_obj)
						self.db.log_buildRequest(build_request_obj)
						#print "SENDING REQUEST WITH DATA", str(build_req)
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
							#logging.debug("\n____________SENDING %s ____________TO____________ %s", build_req, routing_key)
							logging.debug("SENDING BUILD REQUEST FOR JOB ID %i %s %s %s %s %s %s",
										new_job.id,
										new_job.packageinstance.package.name,
										new_job.packageinstance.package.version,
										new_job.packageinstance.distribution.name,
										new_job.packageinstance.arch.name,
										new_job.packageinstance.suite.name,
										new_job.packageinstance.format.name)
						else :
							logging.warn("UNABLE TO ROUTE BUILD REQUEST TO %s", routing_key)
					else :
						logging.warn("FAILED TO ADD JOB")
						response.status = "404 - failed to add job."
						return False
					master_flag = False
				else :
					logging.warn("PACKAGE INSTANCE ERROR")
					response.status = "404 - failed to add/retrieve package instance."
					return False
		except Exception as e:
			raise Exception('Error submitting job: ' + str(e))
			response.status = "500 - Error submitting job"
			return False
		return True # success

	def add_message_queue(self, queue, routing_key, chan):
		logging.debug("CREATING %s", chan.queue_declare(queue=queue, durable=True,
										exclusive=False, auto_delete=False))
		logging.debug("BINDING %s, %s, %s", queue, routing_key, chan.queue_bind(queue=queue,
										exchange=pybit.exchange_name, routing_key=routing_key))
		return

	def process_build_environment_architectures(self, suite, requested_arches, requested_environment) :
		logging.debug("REQUESTED ARCHITECTURES: %s, BUILD ENV: %s", requested_arches, requested_environment)

		env_arches_to_build = list()
		supported_build_env_suite_arches = self.db.get_supported_build_env_suite_arches(suite.name)

		if (len(supported_build_env_suite_arches) == 0):
			response.status = "404 - no supported build environments arch combinations for this suite."
		else :
			if ("all" in requested_arches) and ("any" not in requested_arches) :
				# this is an arch-all request so we only need to build for the first supported arch (for each build env)
				logging.debug("ARCH-ALL REQUEST, ONLY BUILD FIRST SUPPORTED ARCH IN EACH BUILD ENV/ARCH COMBINATION MATCHING (%s, %s)", suite.name, requested_environment)
				supported_build_env_name = ""
				for build_env_suite_arch in supported_build_env_suite_arches :
					if ((requested_environment == None) or (requested_environment == build_env_suite_arch.buildenv.name)) :
						if supported_build_env_name != build_env_suite_arch.buildenv.name :
							supported_build_env_name = build_env_suite_arch.buildenv.name
							env_arches_to_build.append(build_env_suite_arch)
							logging.debug("	ADDING (%s, %s, %s, %i)", build_env_suite_arch.suitearch.suite.name, build_env_suite_arch.suitearch.arch.name, build_env_suite_arch.buildenv.name, build_env_suite_arch.suitearch.master_weight)
						else :
							logging.debug("	IGNORING (%s, %s, %s, %i)", build_env_suite_arch.suitearch.suite.name, build_env_suite_arch.suitearch.arch.name, build_env_suite_arch.buildenv.name, build_env_suite_arch.suitearch.master_weight)
					else :
						logging.debug("	IGNORING (%s, %s, %s, %i) DOES NOT MATCH REQUESTED BUILD ENV (%s)", build_env_suite_arch.suitearch.suite.name, build_env_suite_arch.suitearch.arch.name, build_env_suite_arch.buildenv.name, requested_environment)

			elif ("any" in requested_arches) :
				logging.debug("ARCH-ALL-ANY REQUEST, BUILDING FOR ALL SUPPORTED BUILD ENV/ARCH COMBINATIONS MATCHING (%s, %s)", suite.name, requested_environment)
				for build_env_suite_arch in supported_build_env_suite_arches :
					if ((requested_environment == None) or (requested_environment == build_env_suite_arch.buildenv.name)) :
						env_arches_to_build.append(build_env_suite_arch)
						logging.debug("	ADDING (%s, %s, %s, %i)", build_env_suite_arch.suitearch.suite.name, build_env_suite_arch.suitearch.arch.name, build_env_suite_arch.buildenv.name, build_env_suite_arch.suitearch.master_weight)
					else :
						logging.debug("	IGNORING (%s, %s, %s, %i) DOES NOT MATCH REQUESTED BUILD ENV (%s)", build_env_suite_arch.suitearch.suite.name, build_env_suite_arch.suitearch.arch.name, build_env_suite_arch.buildenv.name, requested_environment)
			else :
				logging.debug("SPECIFIC ARCH (%s) BUILD ENV (%s) REQUEST...", requested_arches, requested_environment)
				for build_env_suite_arch in supported_build_env_suite_arches :
					build_env_name = None
					if build_env_suite_arch.buildenv is not None:
						build_env_name = build_env_suite_arch.buildenv.name
					if ((requested_environment == None) or (requested_environment == build_env_name)) \
					and (build_env_suite_arch.suitearch.arch.name in requested_arches) :
						env_arches_to_build.append(build_env_suite_arch)
						logging.debug("	ADDING (%s, %s, %s, %i)", build_env_suite_arch.suitearch.suite.name, build_env_suite_arch.suitearch.arch.name, build_env_suite_arch.buildenv.name, build_env_suite_arch.suitearch.master_weight)
					else :
						logging.debug("	IGNORING (%s, %s, %s, %i)", build_env_suite_arch.suitearch.suite.name, build_env_suite_arch.suitearch.arch.name, build_env_suite_arch.buildenv.name, build_env_suite_arch.suitearch.master_weight)
		return env_arches_to_build

	def process_package(self, name, version) :
		# retrieve existing package or try to add a new one
		package = None
		matching_package_versions = self.db.get_package_byvalues(name,version)
		if len(matching_package_versions) > 0 :
			package = matching_package_versions[0]
			if package.id :
				logging.debug("MATCHING PACKAGE FOUND (%i, %s, %s)", package.id, package.name, package.version)
		else :
			# add new package to db
			package = self.db.put_package(version,name)
			if package.id :
				logging.debug("ADDED NEW PACKAGE (%i, %s, %s)", package.id, package.name, package.version)
			else :
				logging.warn("FAILED TO ADD NEW PACKAGE (%s, %s)", package.name, package.version)
		return package

	def process_packageinstance(self, build_env, arch, package, dist, pkg_format, suite, master) :
		# check & retrieve existing package or try to add a new one
		packageinstance = None
		if self.db.check_specific_packageinstance_exists(build_env, arch, package, dist, pkg_format, suite) :
			# retrieve existing package instance from db
			packageinstance = self.db.get_packageinstance_byvalues(package, build_env, arch, suite, dist, pkg_format)[0]
			if packageinstance.id :
				logging.debug("MATCHING PACKAGE INSTANCE FOUND (%i, MASTER: %s) FOR [%s, %s, %s, %s, %s, %s, %s]", 
							packageinstance.id, packageinstance.master, 
							package.name, package.version, build_env.name, arch.name, dist.name, pkg_format.name, suite.name)
				# Temporarily disable master update for Issue #84, this should not be default behaviour.
#				if packageinstance.master != master :
#					logging.debug("UPDATING PACKAGE INSTANCE MASTER FLAG (%s)", master)
#					self.db.update_packageinstance_masterflag(packageinstance.id,master)
#					packageinstance.master = master
		else :
			# add new package instance to db
			packageinstance = self.db.put_packageinstance(package, build_env, arch, suite, dist, pkg_format, master)
			if packageinstance.id :
				logging.debug("ADDED NEW PACKAGE INSTANCE (%i, MASTER: %s) FOR [%s, %s, %s, %s, %s, %s, %s]", 
							packageinstance.id, packageinstance.master, 
							package.name, package.version, build_env.name, arch.name, dist.name, pkg_format.name, suite.name)
			else :
				logging.warn("FAILED TO ADD NEW PACKAGE INSTANCE FOR [%s, %s, %s, %s, %s, %s, %s]", 
							package.name, package.version, build_env.name, arch.name, dist.name, pkg_format.name, suite.name)
		return packageinstance

	def process_cancel(self, job, chan):
		job_status_history = self.db.get_job_statuses(job.id)
		last_status = job_status_history[-1].status
		build_client = job_status_history[-1].buildclient
		if (len(job_status_history) > 0) and (last_status == "Building") and (build_client != None) :
			cancel_req = jsonpickle.encode(CancelRequest(job,"%s:%s" % (self.settings['web']['hostname'], self.settings['web']['port'])))
			msg = amqp.Message(cancel_req)
			msg.properties["delivery_mode"] = 2
			logging.debug("UNFINISHED JOB ID %i, STATUS: %s, SENDING CANCEL REQUEST TO: %s", job.id, last_status, build_client)
			chan.basic_publish(msg,exchange=pybit.exchange_name,routing_key=build_client)
		else :
			logging.debug("UNFINISHED JOB ID %i, STATUS: %s, UPDATE STATUS TO 'Cancelled'", job.id, last_status)
			self.db.put_job_status(job.id, "Cancelled", build_client)
		return

	def cancel_superceded_jobs(self, new_job) :
		# check for unfinished jobs that might be cancellable
		packageinstance = new_job.packageinstance
		unfinished_jobs_list = self.db.get_unfinished_jobs()
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
							#check build env...
							if (((unfinished_job.packageinstance.build_env is None) and (packageinstance.build_env is None)) or
								(unfinished_job.packageinstance.build_env.id == packageinstance.build_env.id)):
								self.process_cancel(unfinished_job, chan)
#							else :
#								logging.debug("IGNORING UNFINISHED JOB (%i, %s, %s) BUILD ENV DIFFERS", unfinished_job.id, unfinished_job_package_name, unfinished_job_package_version)
#						else :
#							logging.debug("IGNORING UNFINISHED JOB  (%i, %s, %s) DIST/ARCH/SUITE DIFFERS", unfinished_job.id, unfinished_job_package_name, unfinished_job_package_version)
#					else :
#						logging.debug("IGNORING UNFINISHED JOB (%i, %s, %s) VERSION DIFFERS", unfinished_job.id, unfinished_job_package_name, unfinished_job_package_version)
#				else :
#					logging.debug("IGNORING NEW JOB (%i)", unfinished_job.id)
#			else :
#				logging.debug("IGNORING UNFINISHED JOB (%i, %s)", unfinished_job.id, unfinished_job_package_name)
		return

	def cancel_all_builds(self):
		logging.debug("Cancelling all builds!")
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
			logging.debug("Checking if queue exists: %s", build_client)
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
