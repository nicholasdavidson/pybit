#!/usr/bin/python

import jsonpickle
from pybitweb.bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect,request, hook, static_file
from pybitweb.db import Database,myDb
from pybitweb import lookups, buildd, job, package, packageinstance
from pybitweb.controller import Controller,buildController
from pybit.common import load_settings_from_file

settings = load_settings_from_file('web_settings.json')

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
	return template("pybitweb/static/index.htm")

# static resources like CSS and JS
@route('/bootstrap/<filepath:path>', method='GET')
def serve_static_res(filepath):
    	return static_file(filepath, root='./pybitweb/static/bootstrap/')

# static HTML index page
@route('/index.htm', method='GET')
def serve_static_idex():
    	return static_file("index.htm", root='./pybitweb/static/')

# static HTML page listing buildboxes
@route('/buildd.htm', method='GET')
def serve_static_buildboxes():
    	return static_file("buildd.htm", root='./pybitweb/static/')

# static HTML page listing jobs
@route('/job.htm', method='GET')
def serve_static_jobs():
    	return static_file("job.htm", root='./pybitweb/static/')

# static HTML page listing things
@route('/lookups.htm', method='GET')
def serve_static_lookups():
    	return static_file("lookups.htm", root='./pybitweb/static/')

# static HTML page listing packages
@route('/package.htm', method='GET')
def serve_static_packages():
    	return static_file("package.htm", root='./pybitweb/static/')

# static HTML page listing package instances
@route('/packageinstance.htm', method='GET')
def serve_static_package_instances():
    	return static_file("packageinstance.htm", root='./pybitweb/static/')
try:
	debug(settings['webserver_debug'])
	run(host=settings['webserver_hostname'], port=settings['webserver_port'], reloader=settings['webserver_reloader'])
except Exception as e:
		raise Exception('Error starting web server: ' + str(e))
