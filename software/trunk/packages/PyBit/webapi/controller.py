#!/usr/bin/python

from bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect,request
from amqplib import client_0_8 as amqp
import jsonpickle
import os.path
from db import db

#example CURL command....
#/usr/bin/curl -X POST http://pybit:3000//svn/ --data 
#uri=http://svn.tcl.office/svn/lwdev&directory=software/branches/software_release_chickpea/packages/appbarwidget
#&method=svn
#&distribution=Debian
#&vcs_id=20961
#&architecture_list=all,any
#&package_version=0.6.33chickpea47
#&package=appbarwidget
#&suite=
#&format=deb


class controller:
	
	def __init__(self):
		options =  get_settings("controller.conf")
		myDb = db()

	@route('/create_job', method='POST')
	def createJob():
		uri = request.forms.get('uri')
		method = request.forms.get('method')
		dist = request.forms.get('distribution')
		vcs_id = request.forms.get('vcs_id')
		architectures = request.forms.get('architectures')
		version = request.forms.get('package_version')
		package = request.forms.get('package')
		suite = request.forms.get('suite')
		format = request.forms.get('format')

		transport = transport(method, uri, vcs_id)
		
		supported_architectures = myDb.supportedArchitectures(suite)
		
		if (len(supported_architectures) == 0):
			return

		if (len(architectures) == 1) && (architectures.[0] == "all"):
			instance = packageinstance(suite, package, version, supported_architectures[0], format, dist, transport)
		else 
			for arch in supported_architectures:
				instance = packageinstance(suite, package, version, arch, format, dist, transport)
				if (myDb.contains(package_instance):
					return 0
				else:
					job = job(package_instance)
					#check if database contains a package where status = building, version < package_version, suite = suite 
					# cancel 
					myDb.add(job)
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
