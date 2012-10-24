#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       buildclient.py
#
#       Copyright 2012 Neil Williams <codehelp@debian.org>
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

from amqplib import client_0_8 as amqp
import os
import jsonpickle
import subprocess
import shlex
import pybitclient
import requests
# needs PYTHONPATH=..
import pybit

from pybit.models import ClientMessage

class PyBITClient(object):
	def __init__(self, arch, distribution, format, suite, host, vhost, userid, port,
		password, insist, id, interactive) :
		self.arch = arch
		self.distribution = distribution
		self.suite = suite
		self.format = format
		self.suite = suite
		self.host = host
		self.vhost = vhost
		self.userid = userid
		self.port = port
		self.password = password
		self.insist = insist
		self.id = id
		self.interactive = interactive

		self.routing_key = pybit.get_build_route_name(self.distribution,
			self.arch, self.suite, self.format)

		self.queue_name = pybit.get_build_queue_name(self.distribution,
			self.arch, self.suite, self.format)

		self.client_queue_name = pybit.get_client_queue(self.id)
		print "Connecting with... \nhost: " + self.host + "\nuser id: " + self.userid + "\npassword: "  + self.password + "\nvhost: " + self.vhost + "\ninsist: " + str(self.insist)
		self.conn = amqp.Connection(host=self.host, userid=self.userid, password=self.password, virtual_host=self.vhost, insist= self.insist)
		self.chan = self.conn.channel()

		print "Creating queue with name:" + self.queue_name
		self.chan.queue_declare(queue=self.queue_name, durable=True, exclusive=False, auto_delete=False)
		self.chan.queue_bind(queue=self.queue_name, exchange=pybit.exchange_name, routing_key=self.routing_key)

		print "Creating private command queue with name:" + self.client_queue_name
		self.chan.queue_declare(queue=self.client_queue_name, durable=False, exclusive=True, auto_delete=False)


	def interactive_handler(self, msg, build_req) :
		status = None
		while True:
			user_input = raw_input('''Recived message:
		[A]ccept
		[R]eject
		[B]uilding
		[D]one
		B[l]ock
		[F]ail
		''').lower()
			if user_input == "a":
				self.chan.basic_ack(msg.delivery_tag)
				print "Blindly accepting message..."
				msg = ClientMessage.done
				break
			elif user_input == "r":
				self.chan.basic_recover(True)
				print "Rejecting message."
				break
			elif user_input == "b":
				self.chan.basic_ack(msg.delivery_tag)
				status = ClientMessage.building
				break
			elif user_input == "d":
				self.chan.basic_ack(msg.delivery_tag)
				status = ClientMessage.done
				break
			elif user_input == "l":
				self.chan.basic_ack(msg.delivery_tag)
				status = ClientMessage.blocked
				break
			elif user_input == "f":
				self.chan.basic_ack(msg.delivery_tag)
				status = ClientMessage.failed
				break
			else:
				print "Invalid selection."
		if status is not None:
			print "Marking JOB( id ", unpickled_req.job.id,  ") As ", status
			payload = {'status' : status }
			job_status_url = "http://%s/job/%s" % (unpickled_req.web_host, unpickled_req.job.id)
			r = requests.put(job_status_url, payload)

	def build_handler(self, msg, build_req):
		pass

	def message_handler(self, msg, build_req):
		if self.interactive:
			interactive_handler(msg, build_req)
		else:
			build_handler(msg, build_req)


	def  is_building():
		pass

class VersionControlHandler(object):
	def fetch_source(self):
		pass

	def get_srcdir (self):
		pass

	def clean_source (self, pkg) :
		pass

	# support test cases
	def is_dry_run (self):
		if (not hasattr(self, 'options')) :
			return False
		if (not "dry_run" in self.options) :
			return False
		return self.options["dry_run"]

	def __init__(self):
		self.workdir = ""
		self.options = {}
		try:
			self.options =  pybitclient.get_settings(self)
			if len(self.options) == 0 :
				self.options["dry_run"] = True
				self.options["buildroot"] = "/tmp/buildd"
		except Exception as e:
			raise Exception('Error constructing subversion build client: ' + str(e))
			return

class PackageHandler(object):

	chan = None

	def __init__(self):
		self.build_process = None
		return

	def is_dry_run (self):
		if (not hasattr(self, 'options')) :
			return False
		if (not "dry_run" in self.options) :
			return False
		return self.options["dry_run"]

	def build_master (buildroot):
		pass

	def build_slave (buildroot):
		pass

	def update_environment (self,name,pkg) :
		pass

	def upload (self, dirname, changes, pkg) :
		pass

	def is_building (self) :
		if not self.build_process :
			return False
		if self.build_process.poll() == None :
			return False
		return True

	def cancel (self) :
		try:
			if not self.build_process :
				return
			if self.build_process.poll() == None : # None if still running
				self.build_process.terminate()
		except Exception as e:
			raise Exception('Error cancelling: ' + str(e))
			return
