

def get_client_queue(id):
	return "build_client_%s" % id

def get_build_queue_name(dist, arch, suite, package):
	return "%s_%s_%s_%s" % (dist, arch, suite, package)

def get_build_route_name(dist, arch, suite, package):
	return "%s.%s.%s.%s" % (dist, arch, suite, package)

exchange_name="pybit"
status_route="pybit.control.status"
status_queue="pybit_status"
