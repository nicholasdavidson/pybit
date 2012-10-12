#!/usr/bin/python

from lib.bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect,request
from amqplib import client_0_8 as amqp
import jsonpickle
import os.path

from common.db import db
from common.models import transport, packageinstance, job
# example CURL command....
# /usr/bin/curl -X POST http://localhost:8080/add/ --data uri=http://svn.tcl.office/svn/lwdev&directory=software/branches/software_release_chickpea/packages/appbarwidget&method=svn&distribution=Debian&vcs_id=20961&architecture_list=all,any&package_version=0.6.33chickpea47&package=appbarwidget&suite=&format=deb

myDb = db()

class controller:
	
	def __init__(self):
		#conn = amqp.Connection(host="localhost:5672", userid="guest", password="guest", virtual_host="/", insist=False)
		#chan = conn.channel()
		print "controller init"

	@route('/add', method='POST')
	def add():
		print "create job"
		uri = request.forms.get('uri')
		method = request.forms.get('method')
		dist = request.forms.get('distribution')
		vcs_id = request.forms.get('vcs_id')
		architectures = request.forms.get('architecture_list')
		version = request.forms.get('package_version')
		package = request.forms.get('package')
		suite = request.forms.get('suite')
		format = request.forms.get('format')
		trans = transport(None, method, uri, vcs_id)

		if not uri and method and dist and vcs_id and architectures and version and package and suite and format :
			response.status = "400 - Required fields missing."
			return
#		else : 
#			print uri, method, dist, vcs_id, architectures, version, package, suite, format

		supported_arches = myDb.supportedArchitectures(suite)

		if (len(supported_arches) == 0):
			response.status = "404 - no supported architectures for this suite."
			return

		if (architectures and len(architectures) == 1 and architectures[0] == "all"):
			instance = packageinstance(suite, package, version, supported_arches[0], format, dist, trans)
		else :
			for arch in supported_arches:
				if not myDb.check_specific_packageinstance_exists(arch, dist, format, package, version, suite) :
					instance = packageinstance(suite, package, version, arch, format, dist, trans)
					myJob = job(None,instance,None)
					# check if database contains a package where status = building, version < package_version, suite = suite 
					# myDb.add(myJob)
			# cancel any job older jobs matching this package on queue
		return

	@route('/cancel_all', method='POST')
	def cancelAllBuilds():
		return

	@route('/cancel_package', method='POST')
	def cancelPackage():
		return

	@route('/cancel_package_instance', method='POST')
	def cancelPackageInstance():
		return
