#!/usr/bin/python

from bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect
import jsonpickle
from db import db

import lookups,job,package

myDb = db()

@error(404)
def error404(error):
    return 'HTTP Error 404 - Not Found.'

@error(500)
def error404(error):
    return 'HTTP Error 500 - Internal Server Error.'
    
@route('/', method='GET')
def index():
	#main index page for the whole API
	redirect("/job") #probably what we want

debug(True)
run(host='localhost', port=8080, reloader=True)
