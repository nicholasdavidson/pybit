import re
import os
import errno
import json
import time
import logging
import jsonpickle
from amqplib import client_0_8 as amqp
import pybit
from pybit.models import TaskComplete, PackageInstance, ClientMessage, BuildRequest, CommandRequest, AMQPConnection,\
	CancelRequest
from debianclient import DebianBuildClient
from subversion import SubversionClient
import multiprocessing
import socket
import requests

#       Copyright 2012:
#
#       Nick Davidson <nickd@toby-churchill.com>,
#       Simon Haswell <simonh@toby-churchill.com>,
#       Neil Williams <neilw@toby-churchill.com>,
#       James Bennet <github@james-bennet.com / James.Bennet@toby-churchill.com>

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

class PyBITClient(object):

	def _clean_current(self):
		self.vcs_handler = None
		self.process = None
		self.current_msg = None
		self.current_request = None
		self.overall_success = None

	def set_status(self, status, request=None, client = None):
		if request is None:
			request = self.current_request
		if status is not None and request is not None:
			print "Marking JOB id: %s as: %s" % (request.get_job_id(), status) #FIXME: this clears/resets 'cancelled' state
			payload = {'status' : status }
			if client is not None:
				payload['client']  = client
			job_status_url = "http://%s/job/%s" % (request.web_host, request.get_job_id())
			try:
				requests.put(job_status_url, payload)
			except requests.exceptions.ConnectionError :
				pass
		else:
			print "Couldn't find status or current_request"

	def get_status(self, request = None):
		if request is None:
			request = self.current_request
		if request is not None:
			job_status_get_url = "http://%s/job/%s/status" % (request.web_host, request.get_job_id())
			r = requests.get(job_status_get_url)
			if r.status_code == 200 and r.headers['content-type'] == 'application/json':
				status_list = jsonpickle.decode(r.content)
				if (len(status_list) > 0):
					return status_list[-1].status

	def wait(self):
		time.sleep(5)
		if self.state == "IDLE" :
			msg = self.message_chan.basic_get()
			if msg is not None :
				self.message_handler(msg)

		cmd = self.command_chan.basic_get()
		if cmd is not None:
			self.command_handler(cmd)

	def move_state(self, new_state):
		if (new_state in self.state_table):
			#FIXME: we can stack state handling in here.
			self.old_state = self.state
			self.state = new_state

			if self.state == "CHECKOUT":
				args = (self.current_request,self.conn_info)
				self.process = multiprocessing.Process(target=self.vcs_handler.fetch_source,args=args)
				self.process.start()
				self.set_status(ClientMessage.building,None,self.conn_info.client_name)
			elif self.state == "BUILD":
				# mark this as the moment that the build starts
				self.current_request.stamp_request()
				args = (self.current_request,self.conn_info)
				if self.current_request.job.packageinstance.master == True:
					self.process = multiprocessing.Process(target=self.format_handler.build_master, args=args)
				else:
					self.process = multiprocessing.Process(target=self.format_handler.build_slave, args=args)
				self.process.start()
			elif self.state == "CLEAN":
				args = (self.current_request,self.conn_info)
				self.process = multiprocessing.Process(target=self.vcs_handler.clean_source, args=args)
				self.process.start()
			elif self.state == "UPLOAD":
				args = (self.current_request,self.conn_info)
				self.process = multiprocessing.Process(target=self.format_handler.upload, args=args)
				self.process.start()
			elif self.state == "IDLE":
				overall_success = self.overall_success
				current_msg = self.current_msg
				current_req = self.current_request
				self._clean_current()
				if current_msg is not None :
					self.message_chan.basic_ack(current_msg.delivery_tag)
					if overall_success == True:
						self.set_status(ClientMessage.done, current_req)
					elif overall_success == False:
						self.set_status(ClientMessage.failed, current_req)

			print "Moved from %s to %s" % (self.old_state, self.state)
		else:
			print "Unhandled state: %s" % (new_state)



	def idle_handler(self, msg, decoded):
		if isinstance(decoded, BuildRequest):
			self.current_msg = msg
			self.current_request = decoded
			if (self.current_request.transport.method == "svn" or
				self.current_request.transport.method == "svn+ssh"):
				try:
					if self.get_status() == ClientMessage.waiting:
						self.vcs_handler = SubversionClient(self.settings)
						self.move_state("CHECKOUT")
					elif self.get_status() == ClientMessage.cancelled:
						print "jobid: %s has been cancelled. Acking." % (self.current_request.get_job_id())
						self.move_state("IDLE")
				except Exception as requests.exceptions.ConnectionError:
					self.overall_success = False
					self.move_state("IDLE")
			else:
				self.overall_success = False
				self.move_state("IDLE")

	def fatal_error_handler(self, msg, decoded):
		print "Fatal Error handler"

	def checkout_handler(self, msg, decoded):
		if isinstance(decoded, TaskComplete) :
			self.process.join()

			if decoded.success == True:
				self.move_state("BUILD")
			else:
				self.move_state("CLEAN")



	def build_handler(self, msg, decoded):
		if isinstance(decoded, TaskComplete) :
			self.process.join()

			if decoded.success == True:
				self.move_state("UPLOAD")
			else:
				self.move_state("CLEAN")



	def upload_handler(self, msg, decoded):
		if isinstance(decoded, TaskComplete) :
			self.overall_success = decoded.success
			self.process.join()
			self.move_state("CLEAN")

	def clean_handler(self, msg, decoded):
		if isinstance(decoded, TaskComplete) :
			self.process.join()
			if decoded.success == True:
				self.move_state("IDLE")
			else:
				self.move_state("FATAL_ERROR")

	def __init__(self, arch, distribution, pkg_format, suite, conn_info, settings) :
		self.state_table = {}
		self.state_table["UNKNOWN"] = self.fatal_error_handler
		self.state_table["IDLE"] = self.idle_handler
		self.state_table["FATAL_ERROR"] = self.fatal_error_handler
		self.state_table["CHECKOUT"] = self.checkout_handler
		self.state_table["BUILD"] = self.build_handler
		self.state_table["UPLOAD"] = self.upload_handler
		self.state_table["CLEAN"] = self.clean_handler
		self.overall_success = None
		self.state = "UNKNOWN"
		self.arch = arch
		self.distribution = distribution
		self.pkg_format = pkg_format
		self.suite = suite
		self.conn = None
		self.command_chan = None
		self.message_chan = None
		self.settings = settings

		self.routing_key = pybit.get_build_route_name(self.distribution,
			self.arch, self.suite, self.pkg_format)

		self.queue_name = pybit.get_build_queue_name(self.distribution,
			self.arch, self.suite, self.pkg_format)

		self.conn_info = conn_info



		#self.message_chan.basic_consume(queue=self.queue_name, no_ack=False, callback=self.message_handler, consumer_tag="build_callback")
		#self.command_chan.basic_consume(queue=self.client_queue_name, no_ack=True, callback=self.command_handler, consumer_tag="cmd_callback")



		if (pkg_format == "deb") :
			self.format_handler = DebianBuildClient(self.settings)
		else:
			print "Empty build client"
			self.format_handler = None

		self._clean_current()
		self.move_state("IDLE")

	def message_handler(self, msg):
		build_req = jsonpickle.decode(msg.body)
		if not isinstance(build_req, BuildRequest) :
			self.message_chan.basic_ack(msg.delivery_tag)
			return
		if self.process:
			print "Detected a running process"
		self.state_table[self.state](msg, build_req)

	def command_handler(self, msg):
		cmd_req = jsonpickle.decode(msg.body)
		if (not isinstance(cmd_req, TaskComplete) and
			not isinstance(cmd_req, CommandRequest)):
			print "Can't handle message type."
			self.command_chan.basic_ack(msg.delivery_tag)
		elif isinstance(cmd_req, CommandRequest) :
			if isinstance(cmd_req, CancelRequest) :
				print "Received CANCEL request for jobid:", cmd_req.get_job_id()
				self.set_status(ClientMessage.cancelled, cmd_req)
				if (self.current_request.get_job_id() == cmd_req.get_job_id()) and (self.process is not None) :
					self.process.terminate()
					self.process.join()
					self.process = None
					self.move_state("IDLE")
			else :
				print "Received COMMAND request for jobid:", cmd_req.get_job_id()
		else:
			self.state_table[self.state](msg, cmd_req)

	def is_building(self):
		if self.format_handler.is_building() :
			# FIXME
			return True
		return False

	def connect(self):
		try:
			self.conn = amqp.Connection(host=self.conn_info.host,
				userid=self.conn_info.userid, password=self.conn_info.password,
				virtual_host=self.conn_info.vhost, insist=False)
			self.command_chan = self.conn.channel()
			self.message_chan = self.conn.channel()
			self.message_chan.basic_qos(0,1,False)
		except socket.error as e:
			print "Couldn't connect rabbitmq server with: %s" % repr(self.conn_info)
			return

		print "Creating queue with name:" + self.queue_name
		self.message_chan.queue_declare(queue=self.queue_name, durable=True,
			exclusive=False, auto_delete=False)
		self.message_chan.queue_bind(queue=self.queue_name,
			exchange=pybit.exchange_name, routing_key=self.routing_key)

		print "Creating private command queue with name:" + self.conn_info.client_name
		self.command_chan.queue_declare(queue=self.conn_info.client_name,
			durable=False, exclusive=True, auto_delete=False)
		self.command_chan.queue_bind(queue=self.conn_info.client_name,
			exchange=pybit.exchange_name, routing_key=self.conn_info.client_name)


	def disconnect(self):
		if self.conn:
			if self.command_chan:
				#self.command_chan.basic_cancel("build_callback")
				try:
					self.command_chan.close()
				except socket.error :
					pass
			if self.message_chan:
				#self.message_chan.basic_cancel("build_callback")
				try:
					self.message_chan.close()
				except socket.error :
					pass
			try :
				self.conn.close()
			except socket.error :
				pass


	def __enter__(self):
		self.connect()
		return self

	def __exit__(self, type, value, traceback):
		self.disconnect()


def run_cmd (cmd, simulate, logfile):
	log = logging.getLogger( "pybit-client" )
	if simulate == True :
		log.debug ("I: Simulating: %s" % cmd)
		return True
	else:
		log.debug("Running: %s" % cmd)
		if logfile is not None :
			command = cmd
			cmd = "%s >> %s 2>&1" % (command, logfile)
		if os.system (cmd) :
			log.debug("%s returned error" % cmd)
			return False
	return True

def send_message (conn_data, msg) :
	conn = None
	chan = None
	if conn_data is not None:
		conn = amqp.Connection(host=conn_data.host, userid=conn_data.userid,
			password=conn_data.password, virtual_host=conn_data.vhost, insist=True)
		chan = conn.channel()
	task = None
	if msg == "success":
		task = TaskComplete(msg, True)
	else:
		task = TaskComplete(msg, False)
	if conn and chan:
		chan.basic_publish(amqp.Message(task.toJson()),exchange=pybit.exchange_name,
			routing_key=conn_data.client_name)
		chan.close()
		conn.close()
	else :
		log = logging.getLogger( "pybit-client" )
		log.debug("I: Simulating sending message: %s " % (msg))

def get_settings(path):
	try:
		ret = {}
		if (type(path) != str) :
			# passed self or some other object, assume default
			path = "client.conf"
		if (os.path.isfile(path)):
			pass
		elif os.path.isfile ("/etc/pybit/client/client.conf") :
			path = "/etc/pybit/client/client.conf"
		else :
			return ret
	except Exception as e:
			raise Exception('Cannot access path to config file: ' +  str(e))
			return
	try:
		fh = open(path,"r")
		file_contents = fh.read();
		return json.loads(file_contents)
	except IOError as e:
		raise Exception("Cannot open config file for reading: " +  str(e))
		return
	except Exception as e:
		raise Exception("Unhandled JSON error" + str(e))
		return

def mkdir_p(path):
	try:
		os.makedirs(path)
	except OSError as exc: # Python >2.5
		if exc.errno == errno.EEXIST:
			pass
		else:
			raise Exception("Exception" + str(exc))
			return

