
import re
import os
import errno
import json
import jsonpickle
from amqplib import client_0_8 as amqp
import pybit
from pybit.models import TaskComplete, PackageInstance, ClientMessage, BuildRequest, CommandRequest, AMQPConnection
from debian import DebianBuildClient
from subversion import SubversionClient
import multiprocessing

class PyBITClient(object):

	def wait(self):
		if self.state == "IDLE":
			self.chan.wait(allowed_methods=(self.message_handler))
		else:
			self.chan.wait(allowed_methods=(self.command_handler))

	def move_state(self, new_state):
		if (new_state in self.state_table):
			#FIXME: we can stack state handling in here.
			self.old_state = self.state
			self.state = new_state
			if self.state == "CHECKOUT":
				args = (self.current_request,self.conn_info)
				self.process = multiprocessing.Process(target=self.vcs_handler.fetch_source,args=args)
				self.process.start()
			elif self.state == "BUILD":
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
				self.overall_success = None
				self.current_request = None
				self.process = None
				self.current_msg = None
				if (overall_success is not None and current_msg is not None) :
					print "Acking: %s" % current_msg.delivery_tag
					self.chan.basic_ack(current_msg.delivery_tag)
					#FIXME: need to post job id

			print "Moved from %s to %s" % (self.old_state, self.state)
		else:
			print "Unhandled state: %s" % (new_state)



	def idle_handler(self, msg, decoded):
		if isinstance(decoded, BuildRequest):

			self.current_msg = msg
			self.current_request = decoded
			if (self.current_request.transport.method == "svn" or
				self.current_request.transport.method == "svn+ssh"):
				self.vcs_handler = SubversionClient()
				self.move_state("CHECKOUT")
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

	def __init__(self, arch, distribution, pkg_format, suite, host, vhost, userid, port,
		password, insist, clientid) :
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
		self.host = host
		self.vhost = vhost
		self.userid = userid
		self.port = port
		self.password = password
		self.insist = insist
		self.clientid = clientid

		self.routing_key = pybit.get_build_route_name(self.distribution,
			self.arch, self.suite, self.pkg_format)

		self.queue_name = pybit.get_build_queue_name(self.distribution,
			self.arch, self.suite, self.pkg_format)

		self.client_queue_name = pybit.get_client_queue(self.clientid)

		self.conn_info = AMQPConnection(self.client_queue_name,self.host,
			self.userid, self.password, self.vhost)

		print "Connecting with... \nhost: " + self.host + "\nuser id: " + self.userid + "\npassword: "  + self.password + "\nvhost: " + self.vhost + "\ninsist: " + str(self.insist)
		self.conn = amqp.Connection(host=self.host, userid=self.userid, password=self.password, virtual_host=self.vhost, insist= self.insist)
		self.chan = self.conn.channel()

		print "Creating queue with name:" + self.queue_name
		
		self.chan.queue_declare(queue=self.queue_name, durable=True, exclusive=False, auto_delete=False)
		self.chan.queue_bind(queue=self.queue_name, exchange=pybit.exchange_name, routing_key=self.routing_key)

		print "Creating private command queue with name:" + self.client_queue_name
		self.chan.queue_declare(queue=self.client_queue_name, durable=False, exclusive=True, auto_delete=False)
		self.chan.queue_bind(queue=self.client_queue_name, exchange=pybit.exchange_name, routing_key=self.client_queue_name)
		if (pkg_format == "deb") :
			self.format_handler = DebianBuildClient()
		else:
			print "Empty build client"
			self.format_handler = None
		self.vcs_handler = None
		self.process = None
		self.current_msg = None
		self.move_state("IDLE")

	def message_handler(self, msg):
		print "message handler got: %s" % msg.delivery_tag
		build_req = jsonpickle.decode(msg.body)
		if not isinstance(build_req, BuildRequest) :
			self.chan.basic_ack(msg.delivery_tag)
			return
		if self.process:
			print "Detected a running process"
		self.state_table[self.state](msg, build_req)

	def command_handler(self, msg):
		print "command handler got: %s" % msg.delivery_tag
		cmd_req = jsonpickle.decode(msg.body)
		if (not isinstance(cmd_req, TaskComplete) and
			not isinstance(cmd_req, CommandRequest)):
			print "Can't handle message type."
			self.chan.basic_ack(msg.delivery_tag)
		else:
			self.state_table[self.state](msg, cmd_req)

	def is_building(self):
		if self.format_handler.is_building() :
			# FIXME
			return True
		return False


def run_cmd (cmd, simulate):
	if simulate == True :
		print "Simulating: %s" % cmd
		return True
	else:
		if not os.system (cmd) :
			return False
	return True

def send_message (conn_data, msg) :
	conn = amqp.Connection(host=conn_data.host, userid=conn_data.userid,
		password=conn_data.password, virtual_host=conn_data.vhost, insist=True)
	chan = conn.channel()
	task = None
	if msg == "success":
		task = TaskComplete(msg, True)
	else:
		task = TaskComplete(msg, False)
	chan.basic_publish(amqp.Message(task.toJson()),exchange=pybit.exchange_name,
		routing_key=conn_data.client_name)
	chan.close()
	conn.close()

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

