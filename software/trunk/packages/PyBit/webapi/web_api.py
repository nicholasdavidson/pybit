#!/usr/bin/python

from bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect,request
import jsonpickle
from db import db
from controller import Controller

import buildd,forms,job,lookups,package, reports

myDb = db()
#buildController = controller()

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

debug(True)
run(host='localhost', port=8080, reloader=True)
