#!/usr/bin/python

#       pybit-web
#       Copyright 2012:
#
#	Nick Davidson <nickd@toby-churchill.com>,
#	Simon Haswell <simonh@toby-churchill.com>,
#	Neil Williams <neilw@toby-churchill.com>,
#	James Bennet <github@james-bennet.com / James.Bennet@toby-churchill.com>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

from pybitweb.bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect,request, hook, static_file
from pybitweb.common import load_settings_from_file,app

settings = load_settings_from_file('web_settings.json')

@app.error(404)
def error404(error):
    return 'HTTP Error 404 - Not Found.'

# Remove this to get more debug.
@app.error(500)
def error404(error):
    return 'HTTP Error 500 - Internal Server Error.'

# Things in here are applied to all requests. We need to set this header so strict browsers can query it using jquery
#http://en.wikipedia.org/wiki/Cross-origin_resource_sharing
@app.hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'

@app.route('/', method='GET')
def index():
	return template("pybitweb/static/index.htm", host=settings['webserver_hostname'], port=settings['webserver_port'],protocol=settings['webserver_protocol'])

@app.route('/settings.json', method='GET')
def js_settings():
	response.content_type = "application/json"
	return static_file("settings.json", root='./pybitweb/static/')

# static resources like CSS
@app.route('/bootstrap/<filepath:path>', method='GET')
def serve_static_res(filepath):
    	return static_file(filepath, root='./pybitweb/static/bootstrap/')

# static HTML index page
@app.route('/index.htm', method='GET')
def serve_static_idex():
    	return template("pybitweb/static/index.htm", host=settings['webserver_hostname'], port=settings['webserver_port'],protocol=settings['webserver_protocol'])

# static HTML page listing buildboxes
@app.route('/buildd.htm', method='GET')
def serve_static_buildboxes():
    	return template("pybitweb/static/buildd.htm", host=settings['webserver_hostname'], port=settings['webserver_port'],protocol=settings['webserver_protocol'])

# static HTML page listing jobs
@app.route('/job.htm', method='GET')
def serve_static_jobs():
    	return template("pybitweb/static/job.htm", host=settings['webserver_hostname'], port=settings['webserver_port'],protocol=settings['webserver_protocol'])

# static HTML page listing things
@app.route('/lookups.htm', method='GET')
def serve_static_lookups():
    	return template("pybitweb/static/lookups.htm", host=settings['webserver_hostname'], port=settings['webserver_port'],protocol=settings['webserver_protocol'])

# static HTML page listing packages
@app.route('/package.htm', method='GET')
def serve_static_packages():
    	return template("pybitweb/static/package.htm", host=settings['webserver_hostname'], port=settings['webserver_port'],protocol=settings['webserver_protocol'])

# static HTML page listing package instances
@app.route('/packageinstance.htm', method='GET')
def serve_static_package_instances():
    	return template("pybitweb/static/packageinstance.htm", host=settings['webserver_hostname'], port=settings['webserver_port'],protocol=settings['webserver_protocol'])
