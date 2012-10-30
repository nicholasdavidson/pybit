
import re
import os
import errno
import json
import jsonpickle
from amqplib import client_0_8 as amqp
import pybit
from pybit.models import TaskComplete

def run_cmd (cmd, simulate):
	if simulate == True :
		print cmd
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

