#!/usr/bin/python

from bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect

@route('/forms', method='GET')
def index():
	# menu, probably what we want
	return '''<h4>Data entry forms for lookup tables</h4>
				<ul>
				<li><a href='/forms/arch'>Package Architectures</a></li>
				<li><a href='/forms/status'>Job Statuses</a></li>
				<li><a href='/forms/dist'>Software Distributions</a></li>
				<li><a href='/forms/format'>Package Formats</a></li>
				<li><a href='/forms/suite'>Software Suites</a></li>
				</ul>
				'''
#<<<<<<<< Lookup table forms >>>>>>>

@route('/forms/arch', method='GET')
def login_form():
	return '''<form method="PUT" action="/arch">
				<h4>Package Architectures</h4>
				<label for="id">ID</label>
				<input name="id" type="text" />
				<label for="name">Name</label>
				<input name="name" type="name" />
				<input type="submit" />
				</form>'''

@route('/forms/status', method='GET')
def login_form():
	return '''<form method="PUT" action="/status">
				<h4>Job Statuses</h4>
				<label for="id">ID</label>
				<input name="id" type="text" />
				<label for="name">Name</label>
				<input name="name" type="name" />
				<input type="submit" />
				</form>'''

@route('/forms/dist', method='GET')
def login_form():
	return '''<form method="PUT" action="/dist">
				<h4>Software Distributions</h4>
				<label for="id">ID</label>
				<input name="id" type="text" />
				<label for="name">Name</label>
				<input name="name" type="name" />
				<input type="submit" />
				</form>'''

@route('/forms/format', method='GET')
def login_form():
	return '''<form method="PUT" action="/format">
				<h4>Package Formats</h4>
				<label for="id">ID</label>
				<input name="id" type="text" />
				<label for="name">Name</label>
				<input name="name" type="name" />
				<input type="submit" />
				</form>'''

@route('/forms/suite', method='GET')
def login_form():
	return '''<form method="PUT" action="/suite">
				<h4>Software Suites</h4>
				<label for="id">ID</label>
				<input name="id" type="text" />
				<label for="name">Name</label>
				<input name="name" type="name" />
				<input type="submit" />
				</form>'''
