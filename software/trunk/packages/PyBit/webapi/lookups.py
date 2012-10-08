#!/usr/bin/python

from bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect
import jsonpickle
from db import db

myDb = db()

@route('/arch', method='GET')
def get_arch():
	response.content_type = "application/json"
	#return list of arches
	return jsonpickle.encode(myDb.get_arches());
	
@route('/status', method='GET')
def get_statuses():
	response.content_type = "application/json"
	#return list of statuses
	return jsonpickle.encode(myDb.get_statuses());

@route('/dist', method='GET')
def get_dists():
	response.content_type = "application/json"
	#return list of distributions
	return jsonpickle.encode(myDb.get_distributions());

@route('/format', method='GET')
def get_formats():
	response.content_type = "application/json"
	#return list of package formats
	return jsonpickle.encode(myDb.get_formats());

@route('/suite', method='GET')
def get_suites():
	response.content_type = "application/json"
	#return list of suites
	return jsonpickle.encode(myDb.get_suites());
