
import re
import os
import errno
import json
import jsonpickle

def get_settings(path):
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
	try:
		fh = open(path,"r")
		file_contents = fh.read();
		return json.loads(file_contents)
	except IOError:
		raise Exception, "Cannot open config file for reading."
		return
	except Exception:
		raise Exception,"Unhandled JSON error"
		return

def mkdir_p(path):
	if (type(path) != str):
		raise Exception,"Need a string to make directories by path"
	try:
		os.makedirs(path)
	except OSError as exc: # Python >2.5
		if exc.errno == errno.EEXIST:
			pass
		else: raise

class deb_package:
	def __init__(self,msg_body=''):
		if msg_body:
			self = jsonpickle.decode (msg_body)
