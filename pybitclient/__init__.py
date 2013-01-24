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


import re
import os
import imp
import errno
import json
import time
import logging
import jsonpickle
from amqplib import client_0_8 as amqp
import pybit
from pybit.models import TaskComplete, PackageInstance, ClientMessage, BuildRequest, CommandRequest, AMQPConnection,\
	CancelRequest
from pybitclient.buildclient import PackageHandler, VersionControlHandler
import multiprocessing
import socket
import requests
from requests.auth import HTTPBasicAuth

class PyBITClient(object):

	def _clean_current(self):
		self.vcs_handler = None
		self.process = None
		self.current_msg = None
		self.current_request = None
		self.overall_success = None
		self.subprocess_message = None

	def set_status(self, status, request=None, client = None):
		if request is None:
			request = self.current_request
		if status is not None and request is not None:
			logging.debug ("Marking JOB id: %s as: %s" % (request.get_job_id(), status)) #FIXME: this clears/resets 'cancelled' state
			payload = {'status' : status }
			if client is not None:
				payload['client']  = client
			job_status_url = "http://%s/job/%s" % (request.web_host, request.get_job_id())
			try:
				requests.put(job_status_url, payload, auth=HTTPBasicAuth('admin', 'pass'))
			except requests.exceptions.ConnectionError :
				pass
		else:
			logging.debug ("Couldn't find status or current_request")


	def get_status(self, request = None):
		"""Get the build request status from the controller via REST

Returns the current job status, waiting if the controller cannot be
contacted or None if the job doesn't exist

"""
		if request is None:
			request = self.current_request
		if request is not None:
			job_status_get_url = "http://%s/job/%s/status" % (request.web_host, request.get_job_id())
			r = requests.get(job_status_get_url)
			if r.status_code == 200 and r.headers['content-type'] == 'application/json':
				status_list = jsonpickle.decode(r.content)
				if (len(status_list) > 0):
					return status_list[-1].status
			elif r.status_code == 404:
				return None
			else:
				return ClientMessage.waiting

	def republish_job(self, buildreq):
		if (isinstance(buildreq, BuildRequest)) :
			routing_key = pybit.get_build_route_name(buildreq.get_dist(),
				buildreq.get_arch(),
				buildreq.get_suite(),
				buildreq.get_format())
			try:
				msg = jsonpickle.encode(buildreq)
				self.message_chan.basic_publish(amqp.Message(msg),
					exchange=pybit.exchange_name,
					routing_key=routing_key,
					mandatory=True)
			except amqp.AMQPConnectionException as e:
				logging.debug("Couldn't connect to channel. traceback: %s" % e)
	def wait(self):
		time.sleep(self.poll_time)
		if self.state == "IDLE" :
			msg = None
			if self.message_chan is not None:
				for suite in self.listen_list:
					msg = self.message_chan.basic_get(queue=self.listen_list[suite]['queue'])
					if msg:
						break
			if msg is not None :
				self.message_handler(msg)
		cmd = None
		if self.command_chan is not None :
			cmd = self.command_chan.basic_get(no_ack=True)
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
				subprocess_message = self.subprocess_message
				self._clean_current()
				if current_msg is not None :
					self.message_chan.basic_ack(current_msg.delivery_tag)
					if overall_success == True:
						self.set_status(ClientMessage.done, current_req)
					elif overall_success == False:
						if  subprocess_message == 'build-dep-wait':
							self.set_status(ClientMessage.blocked, current_req)
							self.republish_job(current_req)
						else:
							self.set_status(ClientMessage.failed, current_req)
			elif self.state == "FATAL_ERROR":
				current_req = self.current_request
				current_msg = self.current_msg
				self._clean_current()
				self.message_chan.basic_ack(current_msg.delivery_tag)
				self.set_status(ClientMessage.failed, current_req)
				self.republish_job(current_req)

			logging.debug ("Moved from %s to %s" % (self.old_state, self.state))
		else:
			logging.debug ("Unhandled state: %s" % (new_state))

	def plugin_handler (self):
		plugin = None
		vcs = None
		client = None
		plugins = []
		plugin_dir = "/var/lib/pybit-client.d/"
		if not os.path.exists (plugin_dir):
			plugin_dir = os.path.realpath ("./pybitclient/")
		for name in os.listdir(plugin_dir):
			if name.endswith(".py"):
				plugins.append(name.strip('.py'))
		for name in plugins :
			if (name == "buildclient" or name == "__init__"):
				continue
			plugin_path = [ plugin_dir ];
			fp, pathname, description = imp.find_module(name, plugin_path)
			try:
				mod = imp.load_module(name, fp, pathname, description)
				if not (hasattr(mod, 'createPlugin')) :
					logging.error ("Error: plugin path contains an unrecognised module '%s'." % (name))
					return
				plugin = mod.createPlugin(self.settings)
				if (hasattr(plugin, 'get_distribution') and plugin.get_distribution() is not None) :
					client = plugin
				elif (hasattr(plugin, 'method') and plugin.method is not None) :
					vcs = plugin
				else :
					logging.error ("Error: plugin path contains a recognised plugin but the plugin API for '%s' is incorrect." % (name))
					return
			finally:
				# Since we may exit via an exception, close fp explicitly.
				if fp:
					fp.close()
			if client:
				name = client.get_distribution()
				if (name not in self.distros) :
					self.distros[name] = client
			if vcs :
				if (vcs.method not in self.handlers) :
					self.handlers[vcs.method] = vcs;
		logging.info ("List of available handlers: %s" % list(self.handlers.keys()))
		logging.info ("List of available distributions: %s" % list(self.distros.keys()))

	def idle_handler(self, msg, decoded):
		if isinstance(decoded, BuildRequest):
			self.current_msg = msg
			self.current_request = decoded
			try:
				status = self.get_status()
				if (status == ClientMessage.waiting or
					status == ClientMessage.blocked):
					self.vcs_handler = self.handlers[self.current_request.transport.method]
					if (self.vcs_handler is None):
						self.overall_success = False
						self.move_state("IDLE")
						return
					self.move_state("CHECKOUT")
				elif status == None:
					self.move_state("IDLE")
				elif status == ClientMessage.cancelled:
					logging.debug ("jobid: %s has been cancelled. Acking." % self.current_request.get_job_id())
					self.move_state("IDLE")
			except Exception as requests.exceptions.ConnectionError:
				self.overall_success = False
				self.move_state("IDLE")

	def fatal_error_handler(self, msg, decoded):
		logging.debug ("Fatal Error handler")

	def checkout_handler(self, msg, decoded):
		if isinstance(decoded, TaskComplete) :
			self.process.join()

			if decoded.success == True:
				self.move_state("BUILD")
			else:
				self.overall_success = False
				self.move_state("CLEAN")



	def build_handler(self, msg, decoded):
		if isinstance(decoded, TaskComplete) :
			self.process.join()

			if decoded.success == True:
				self.move_state("UPLOAD")
			else:
				self.overall_success = False
				self.subprocess_message = decoded.message
				self.move_state("CLEAN")



	def upload_handler(self, msg, decoded):
		if isinstance(decoded, TaskComplete) :
			self.overall_success = decoded.success
			self.subprocess_message = decoded.message
			self.process.join()
			self.move_state("CLEAN")

	def clean_handler(self, msg, decoded):
		if isinstance(decoded, TaskComplete) :
			self.process.join()
			if decoded.success == True:
				self.move_state("IDLE")
			else:
				self.overall_success = False
				self.move_state("FATAL_ERROR")

	def __init__(self, arch, distribution, pkg_format, suites, conn_info, settings) :
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
		self.listen_list = dict()
		self.conn = None
		self.command_chan = None
		self.message_chan = None
		self.settings = settings
		self.poll_time = 60
		self.distros = {}
		self.handlers = {}
		if 'poll_time' in self.settings:
			self.poll_time = self.settings['poll_time']
		for suite in suites:
			route = pybit.get_build_route_name(self.distribution,
				self.arch, suite, self.pkg_format)
			queue = pybit.get_build_queue_name(self.distribution,
					self.arch, suite, self.pkg_format)
			self.listen_list[suite] = {
				'route': route,
				'queue': queue}
		self.plugin_handler ()
		self.conn_info = conn_info

		if (self.distribution in self.distros):
			self.format_handler = self.distros[self.distribution]
			logging.info ("Using %s build client" % self.distribution)
		elif (self.pkg_format == "deb" and "Debian" in self.distros) :
			self.format_handler = self.distros['Debian']
			logging.warning ("Using default Debian build client for %s package format" % self.pkg_format)
		else:
			logging.debug ("Empty build client")
			self.format_handler = None

		self._clean_current()
		self.move_state("IDLE")

	def message_handler(self, msg):
		build_req = jsonpickle.decode(msg.body)
		if not isinstance(build_req, BuildRequest) :
			self.message_chan.basic_ack(msg.delivery_tag)
			return
		if self.process:
			logging.debug ("Detected a running process")
		self.state_table[self.state](msg, build_req)

	def command_handler(self, msg):
		cmd_req = jsonpickle.decode(msg.body)
		if (not isinstance(cmd_req, TaskComplete) and
			not isinstance(cmd_req, CommandRequest)):
			logging.debug ("Can't handle message type.")
			self.command_chan.basic_ack(msg.delivery_tag)
		elif isinstance(cmd_req, CommandRequest) :
			if isinstance(cmd_req, CancelRequest) :
				logging.debug ("Received CANCEL request for jobid:", cmd_req.get_job_id())
				self.set_status(ClientMessage.cancelled, cmd_req)
				if (self.current_request and
					self.current_request.get_job_id() == cmd_req.get_job_id() and
					self.process is not None) :
					self.process.terminate()
					self.process.join()
					self.process = None
					self.move_state("IDLE")
				else:
					logging.debug("Ignoring cancel request as no current request or id doesn't match.")
			else :
				logging.debug ("Received COMMAND request for jobid:", cmd_req.get_job_id())
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
			self.command_chan.exchange_declare(exchange=pybit.exchange_name, type="direct", durable=True, auto_delete=False)

		except socket.error as e:
			logging.debug ("Couldn't connect rabbitmq server with: %s" % repr(self.conn_info))
			return False

		for suite, info in self.listen_list.items():
			logging.debug("Creating queue with name:" + info['queue'])
			try:
				self.message_chan.queue_declare(queue=info['queue'], durable=True,
					exclusive=False, auto_delete=False)
				self.message_chan.queue_bind(queue=info['queue'],
					exchange=pybit.exchange_name, routing_key=info['route'])
			except amqp.exceptions.AMQPChannelException :
				logging.debug ("Unable to declare or bind to message channel.")
				return False

		logging.debug ("Creating private command queue with name:" + self.conn_info.client_name)
		try:
			self.command_chan.queue_declare(queue=self.conn_info.client_name,
				durable=False, exclusive=True, auto_delete=True)
			self.command_chan.queue_bind(queue=self.conn_info.client_name,
				exchange=pybit.exchange_name, routing_key=self.conn_info.client_name)
		except amqp.exceptions.AMQPChannelException :
			logging.debug (
				"Unable to declare or bind to command channel %s. Does this client already exist?"
				 % (self.conn_info.client_name, ))
			return False
		return True


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
		if self.connect():
			return self
		else:
			return None

	def __exit__(self, type, value, traceback):
		self.disconnect()

# returns zero on success or the exit value of the command.
def run_cmd (cmd, simulate, logfile):
	ret = 0
	if simulate == True :
		logging.debug ("I: Simulating: %s" % cmd)
	else:
		logging.debug("Running: %s" % cmd)
		if logfile is not None :
			command = cmd
			cmd = "%s >> %s 2>&1" % (command, logfile)
		ret = os.system (cmd) >> 8
		if (ret) :
			logging.debug("%s returned error: %d" % (cmd, ret))
	return ret

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
		logging.debug("I: Simulating sending message: %s " % (msg))

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

