#!/usr/bin/python

import jsonpickle
from pybitweb.bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect,request, hook
from pybitweb.db import Database,myDb
from pybitweb import forms, lookups, buildd, job, package, packageinstance
from pybitweb.controller import Controller,buildController

def load_settings_from_file(path):
	settings_file = open(path, 'r')
	encoded_string = settings_file.read()
	settings = jsonpickle.decode(encoded_string )
	return settings

settings = load_settings_from_file('configs/web_settings.json')

@error(404)
def error404(error):
    return 'HTTP Error 404 - Not Found.'

# Remove this to get more debug.
@error(500)
def error404(error):
    return 'HTTP Error 500 - Internal Server Error.'

# Things in here are applied to all requests. We need to set this header so strict browsers can query it using jquery
#http://en.wikipedia.org/wiki/Cross-origin_resource_sharing
@hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'

@route('/', method='GET')
def index():
	#main index page for the whole API, composed of forms and reports pages
	return '''<h1>PyBit - python Buildd Integration Toolkit.</h1>''', forms.index()

##route('/add', method='POST') (buildController.add) # job.vcs_hook now handles the input, and passes off to myController.process_job
# example CURL command....
# /usr/bin/curl -X POST http://localhost:8080/add --data "uri=http://svn.tcl.office/svn/lwdev&directory=software/branches/software_release_chickpea/packages/appbarwidget&method=svn&distribution=Debian&vcs_id=20961&architecture_list=all,any&package_version=0.6.33chickpea47&package=appbarwidget&suite=chickpea&format=deb"

##route('/cancel_all', method='POST') (buildController.cancel_all_builds) # moved to job.cancel_jobs
#/usr/bin/curl -X POST http://localhost:8080/cancel_all"

##route('/cancel_package', method='POST') (buildController.cancel_package) # move to package.cancel
#/usr/bin/curl -X POST http://localhost:8080/cancel_package --data "package_version=0.6.33chickpea47&package=appbarwidget"

##route('/cancel_package_instance', method='POST') (buildController.cancel_package_instance)  # moved to job.cancel_job
#/usr/bin/curl -X POST http://localhost:8080/cancel_package_instance --data "job_id=54"

try:
	debug(settings['webserver_debug'])
	run(host=settings['webserver_hostname'], port=settings['webserver_port'], reloader=settings['webserver_reloader'])
except Exception as e:
		raise Exception('Error starting web server: ' + str(e))
