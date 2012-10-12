#!/usr/bin/python

from lib.bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect

#TODO: Package instances

@route('/forms', method='GET')
def index():
	# menu, probably what we want
	return '''
				<h4><a href='/forms'>Data entry forms for lookup tables</a></h4>
				<ul>
				<li><a href='/forms/arch'>Package Architectures</a></li>
				<li><a href='/forms/status'>Job Statuses</a></li>
				<li><a href='/forms/dist'>Software Distributions</a></li>
				<li><a href='/forms/format'>Package Formats</a></li>
				<li><a href='/forms/suite'>Software Suites</a></li>
				</ul>
				<h4><a href='/forms'>Data entry forms for core tables</a></h4>
				<ul>
				<li><a href='/forms/buildd'>Build Boxes</a></li>
				<li><a href='/forms/package'>Packages</a></li>
				<li><a href='/forms/job'>Build Jobs</a></li>
				</ul>
				'''

#<<<<<<<<  Other forms >>>>>>>

@route('/forms/buildd', method='GET')
def buildd_form():
	return '''<form method="POST" action="/buildd">
				<h4>Add a Buildbox</h4>
				<label for="name">Name</label>
				<input name="name" type="text" />
				<input type="submit" />
				</form>'''

@route('/forms/job', method='GET')
def job_form():
	# TODO: make id fields combo boxey lookups.
	return '''<form method="POST" action="/job">
				<h4>Submit a Job</h4>
				<label for="packageinstance_id">packageinstance_id</label>
				<input name="packageinstance_id" type="text" />
				<label for="buildclient_id">buildclient_id</label>
				<input name="buildclient_id" type="text" />
				<input type="submit" />
				</form>'''

@route('/forms/package', method='GET')
def package_form():
	return '''<form method="POST" action="/job">
				<h4>Add a Package</h4>
				<label for="name">name</label>
				<input name="name" type="text" />
				<label for="version">version</label>
				<input name="version" type="text" />
				<input type="submit" />
				</form>'''

#<<<<<<<< Lookup table forms >>>>>>>

@route('/forms/arch', method='GET')
def arch_form():
	return '''<form method="POST" action="/arch">
				<h4>Add Package Architectures</h4>
				<label for="name">Name</label>
				<input name="name" type="text" />
				<input type="submit" />
				</form>'''

@route('/forms/status', method='GET')
def status_form():
	return '''<form method="POST" action="/status">
				<h4>Add Job Statuses</h4>
				<label for="name">Name</label>
				<input name="name" type="text" />
				<input type="submit" />
				</form>'''

@route('/forms/dist', method='GET')
def dist_form():
	return '''<form method="POST" action="/dist">
				<h4>Add Software Distributions</h4>
				<label for="name">Name</label>
				<input name="name" type="text" />
				<input type="submit" />
				</form>'''

@route('/forms/format', method='GET')
def format_form():
	return '''<form method="POST" action="/format">
				<h4>Add Package Formats</h4>
				<label for="name">Name</label>
				<input name="name" type="text" />
				<input type="submit" />
				</form>'''

@route('/forms/suite', method='GET')
def suite_form():
	return '''<form method="POST" action="/suite">
				<h4>Add Software Suites</h4>
				<label for="name">Name</label>
				<input name="name" type="text" />
				<input type="submit" />
				</form>'''
