#!/usr/bin/python

from bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect

from db import Database
#TODO: Package instances

buid_db = Database()

@route('/forms', method='GET')
def index():
	try:
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
					<li><a href='/forms/packageinstance'>Package Instances</a></li>
					<li><a href='/forms/job'>Build Jobs</a></li>
					</ul>
					'''
	except Exception as e:
		raise Exception('Error rendering page: ' + str(e))
		return None

#<<<<<<<<  Other forms >>>>>>>

@route('/forms/buildd', method='GET')
def buildd_form():
	try:
		return '''<form method="POST" action="/buildd">
					<h4>Add a Buildbox</h4>
					<label for="name">Name</label>
					<input name="name" type="text" />
					<input type="submit" />
					</form>'''
	except Exception as e:
		raise Exception('Error rendering page: ' + str(e))
		return None

@route('/forms/packageinstance', method='GET')
def package_instance_form():
	try:

		packages = build_db.get_packages()
		arches = build_db.get_arches()
		suites = build_db.get_suites()
		dists = build_db.get_dists()
		formats = build_db.get_formats()

		# TODO: NEW. master???

		markup = '''<form method="POST" action="/packageinstance">
					<h4>Create a package instance</h4>
					<label for="package_id">package_id</label>
					<select name="package_id">'''

		for i in packages:
			markup = markup + "<option value='" + str(i.id) + "'>" +  str(i.name) + " " + str(i.version) + "</option>"
		markup = markup + '''</select><br/><label for="arch_id">arch_id</label><select name="arch_id">'''

		for i in arches:
			markup = markup + "<option value='" + str(i.id) + "'>" +  str(i.name) + "</option>"
		markup = markup + '''</select><br/><label for="suite_id">suite_id</label><select name="suite_id">'''

		for i in suites:
			markup = markup + "<option value='" + str(i.id) + "'>" +  str(i.name) + "</option>"
		markup = markup + '''</select><br/><label for="dist_id">dist_id</label><select name="dist_id">'''

		for i in dists:
			markup = markup + "<option value='" + str(i.id) + "'>" +  str(i.name) + "</option>"
		markup = markup + '''</select><br/><label for="format_id">format_id</label><select name="format_id">'''

		for i in formats:
			markup = markup + "<option value='" + str(i.id) + "'>" +  str(i.name) + "</option>"
		markup = markup + '''</select>'''

		markup = markup + "	<br/><input type='submit' /></form>"

		return markup
	except Exception as e:
		raise Exception('Error rendering page: ' + str(e))
		return None

@route('/forms/job', method='GET')
def job_form():
	try:

		instances = build_db.get_packageinstances()
		clients = build_db.get_buildclients()

		markup = '''<form method="POST" action="/job">
					<h4>Submit a Job</h4>
					<label for="packageinstance_id">packageinstance_id</label>
					<select name="packageinstance_id">'''

		for i in instances:
			markup = markup + "<option value='" + str(i.id) + "'>" +  str(i.id) + "</option>"

		markup = markup + '''</select><br/>
					<label for="buildclient_id">buildclient_id</label>

					<select name="buildclient_id">'''

		for i in clients:
			markup = markup + "<option value='" + str(i.id) + "'>" +  str(i.name) + "</option>"

		markup = markup + '''</select><br/>

					<input type="submit" />
					</form>'''

		return markup
	except Exception as e:
		raise Exception('Error rendering page: ' + str(e))
		return None

@route('/forms/package', method='GET')
def package_form():
	try:
		return '''<form method="POST" action="/job">
					<h4>Add a Package</h4>
					<label for="name">name</label>
					<input name="name" type="text" />
					<label for="version">version</label>
					<input name="version" type="text" />
					<input type="submit" />
					</form>'''
	except Exception as e:
		raise Exception('Error rendering page: ' + str(e))
		return None

#<<<<<<<< Lookup table forms >>>>>>>

@route('/forms/arch', method='GET')
def arch_form():
	try:
		return '''<form method="POST" action="/arch">
					<h4>Add Package Architectures</h4>
					<label for="name">Name</label>
					<input name="name" type="text" />
					<input type="submit" />
					</form>'''
	except Exception as e:
		raise Exception('Error rendering page: ' + str(e))
		return None

@route('/forms/status', method='GET')
def status_form():
	try:
		return '''<form method="POST" action="/status">
					<h4>Add Job Statuses</h4>
					<label for="name">Name</label>
					<input name="name" type="text" />
					<input type="submit" />
					</form>'''
	except Exception as e:
		raise Exception('Error rendering page: ' + str(e))
		return None

@route('/forms/dist', method='GET')
def dist_form():
	try:
		return '''<form method="POST" action="/dist">
					<h4>Add Software Distributions</h4>
					<label for="name">Name</label>
					<input name="name" type="text" />
					<input type="submit" />
					</form>'''
	except Exception as e:
		raise Exception('Error rendering page: ' + str(e))
		return None

@route('/forms/format', method='GET')
def format_form():
	try:
		return '''<form method="POST" action="/format">
					<h4>Add Package Formats</h4>
					<label for="name">Name</label>
					<input name="name" type="text" />
					<input type="submit" />
					</form>'''
	except Exception as e:
		raise Exception('Error rendering page: ' + str(e))
		return None

@route('/forms/suite', method='GET')
def suite_form():
	try:
		return '''<form method="POST" action="/suite">
					<h4>Add Software Suites</h4>
					<label for="name">Name</label>
					<input name="name" type="text" />
					<input type="submit" />
					</form>'''
	except Exception as e:
		raise Exception('Error rendering page: ' + str(e))
		return None
