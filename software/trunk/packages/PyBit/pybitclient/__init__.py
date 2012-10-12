
import re
import os
import errno
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

def mkdir_p(path):
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
