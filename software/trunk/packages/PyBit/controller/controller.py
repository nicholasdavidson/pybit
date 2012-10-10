#!/usr/bin/python

from bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect,request
import jsonpickle
import os.path
from db import db

options =  get_settings("repository.conf")
working_copy_path = options["working_copy"] # i386

myDb = db()

@route('/svn', method='POST')
@route('/svn', method='PUT')
def svn():
	directory = request.forms.get('directory')
	# update working copy now???
	
	# parse changelog 
	command = "dpkg-parsechangelog -l" + working_copy_path + directory
	# grep output for package name, arch, version and dist
	
	# check control file for arch master/slave
	
	# 
	
	# creat job for each arch, update dB and add to message queue
	
	return jsonpickle.encode(new_job);

