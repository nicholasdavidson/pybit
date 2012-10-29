
import re
import os
import errno
import json
import jsonpickle
from amqplib import client_0_8 as amqp
import pybit

def run_cmd (cmd, pkg, simulate):
	if simulate == True :
		print cmd
		msg = TaskComplete(job.id, None)
	else:
		if not os.system (cmd) :
			msg = TaskComplete(job.id, None)
	chan.basic_publish(msg,pybit.exchange_name,client_name)

def send_message (conn_data, msg) :
	conn = amqp.Connection(host=conn_data.addr_opt, userid=conn_data.userid_opt,
		password=conn_data.pass_opt, virtual_host=conn_data.vhost_opt, insist=False)
	chan = conn.channel()
	chan.basic_publish(amqp.Message(jsonpickle.encode(msg)),exchange=pybit.exchange_name,routing_key=conn_data.key)
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
			raise Exception("Exception" + str(e))
			return

class deb_package:
	def __init__(self,msg_body=''):
		try:
			if msg_body:
				print msg_body
				tmp = json.loads(msg_body)
				self.method_type = tmp['method_type']
				self.format = tmp['format']
				self.uri = tmp['uri']
				self.vcs_id = tmp['vcs_id']
				self.version = tmp['version']
				self.architecture = tmp['architecture']
				self.suite = tmp['suite']
				self.distribution = tmp['distribution']
				self.name = tmp['name']
				#self = jsonpickle.decode (msg_body) # TODO: broken :(
		except Exception as e:
			raise Exception('Cannot construct deb_package: ' + str(e))
			return
