import jsonpickle
import os

def get_client_queue(id):
	return "build_client_%s" % id

def get_build_queue_name(dist, arch, suite, package):
	return "%s_%s_%s_%s" % (dist, arch, suite, package)

def get_build_route_name(dist, arch, suite, package):
	return "%s.%s.%s.%s" % (dist, arch, suite, package)

def load_settings(file):
	settings_file = None
	path = "./configs/%s" % file
	try:	
		settings_file = open(path, 'r')
	except IOError as e:
		path = "/etc/pybit/%s" % file
		try:
			settings_file = open(path)
		except IOError as e:
			pass
	if settings_file: 
		encoded_string = settings_file.read()
		return jsonpickle.decode(encoded_string )
	else:
		return {}

exchange_name="pybit"
status_route="pybit.control.status"
status_queue="pybit_status"
