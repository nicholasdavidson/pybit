
#import common
#import debian

import re
import os
import json
import jsonpickle

def get_settings(path):
	# dumps() serializes a python object to a JSON formatted string.
	# loads() deserializes a JSON formatted string to a python object.
	try:
		fh = open(path,"r")
		file_contents = fh.read();
		return json.loads(file_contents)
	except IOError:
		raise IOError,"Cannot load settings file."
		return
	except Exception:
		raise Exception,"Unhandled JSON error"
		return

class deb_package:

	def __init__(self,msg_body=''):
		if msg_body:
			self = jsonpickle.decode (msg_body)

def send_message (chan, pkg, key):
	msg.amqp.Message(jsonpickle.encode(pkg))
	msg.properties["delivery_mode"] = 2
	chan.basic_publish(msg,exchange=pkg.architecture,routing_key=key)

def run_cmd (cmd, fail_msg, report, simulate):
	if simulate :
		print cmd
		return True
	else:
		if os.system (command) :
			pkg.msgtype = fail_msg
			msg.amqp.Message(jsonpickle.encode(pkg))
			msg.properties["delivery_mode"] = 2
			chan.basic_publish(msg,exchange=pkg.architecture,routing_key=report)
			return False
	return True
