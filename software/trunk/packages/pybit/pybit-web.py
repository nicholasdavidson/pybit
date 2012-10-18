#!/usr/bin/python

import jsonpickle
from pybitweb.bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect,request
from pybitweb.db import db
from pybitweb import buildd,forms,job,lookups,reports
from pybit.models import package,packageinstance
from pybitweb.controller import controller

myDb = db()
buildController = controller(myDb)

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
	debug(settings['debug'])
	run(host=settings['host'], port=settings['port'], reloader=settings['reloader'])
except Exception as e:
		raise Exception('Error starting web server: ' + str(e))
