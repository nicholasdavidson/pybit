#!/usr/bin/python

from bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect
from db import db
import jsonpickle

myDb = db()

@route('/report', method='GET')
def index():
	try:
		return '''
			<h4><a href='/report'>These are available reports:</a></h4>
			<ul>
				<li><a href='/report/arch'>Package Architectures</a></li>
				<li><a href='/report/status'>Job Statuses</a></li>
				<li><a href='/report/dist'>Software Distributions</a></li>
				<li><a href='/report/format'>Package Formats</a></li>
				<li><a href='/report/suite'>Software Suites</a></li>
				<li><a href='/report/package'>Packages</a></li>
				<li><a href='/report/job'>Jobs</a></li>
			</ul>
		'''
	except Exception as e:
		raise Exception('Error rendering page: ' + str(e))
		return None

@route('/report/package', method='GET')
def report_package() :
	try:
		response.content_type = "application/json"
		return jsonpickle.encode(myDb.get_report_package_instance())
	except Exception as e:
		raise e
		return None
		
@route('/report/suitearches/<suite>', method='GET')
def report_suitearches(suite) :
	try:
		response.content_type = "application/json"
		return jsonpickle.encode(myDb.supportedArchitectures(suite))
	except Exception as e:
		response.content_type = "text/html"
		raise e
		return None
