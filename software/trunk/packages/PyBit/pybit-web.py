#!/usr/bin/python

import jsonpickle
from pybitweb.bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect,request
from pybitweb.db import db
import pybitweb.buildd
import pybitweb.forms
import pybitweb.job
import pybitweb.lookups
import pybitweb.package
import pybitweb.reports
import pybitweb.packageinstance
from pybitweb.controller import controller

myDb = db()
buildController = controller(myDb)

@error(404)
def error404(error):
    return 'HTTP Error 404 - Not Found.'

# Remove this to get more debug.
#@error(500)
#def error404(error):
#    return 'HTTP Error 500 - Internal Server Error.'

@route('/', method='GET')
def index():
	#main index page for the whole API, composed of forms and reports pages
	return '''<h1>PyBit - python Buildd Integration Toolkit.</h1>''', forms.index() , reports.index()

route('/add', method='POST') (buildController.add)

route('/cancel_all', method='POST') (buildController.cancelAllBuilds)

route('/cancel_package', method='POST') (buildController.cancelPackage)

route('/cancel_package_instance', method='POST') (buildController.cancelPackageInstance)

try:
	debug(True)
	run(host='localhost', port=8080, reloader=False)
except Exception as e:
		raise Exception('Error starting web server: ' + str(e))