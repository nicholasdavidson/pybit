#!/usr/bin/python

from bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect
import jsonpickle
from db import db

myDb = db()

@route('/package', method='GET')
def get_all_packages():
	response.content_type = "application/json"
	# Returning list of all packages
	return jsonpickle.encode(myDb.get_packages());

@route('/package/list', method='GET') # TODO, filter by paramater (request.query.[x])
def get_packages_filtered():
	response.content_type = "application/json"
	#TODO - CODEME
	return "Returning packages by filter"

@route('/package/details/:name:', method='GET')
def get_package_versions(name):
	response.content_type = "application/json"
	#TODO - CODEME
	return template("Returning versions for package {{name}}",name=name)

@route('/package/details/:name:/:version', method='GET')
def get_package_details(name,version):
	response.content_type = "application/json"
	#TODO - CODEME
	return template("Returning details for package {{name}} v{{version}}",name=name, version=version)
