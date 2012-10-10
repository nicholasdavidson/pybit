#!/usr/bin/python

# TODO: Change DB methods and associated HTTP GEThandlers to work on these JSON objects, rather than returning the raw resultsets themselves, which are a pain to deserialise.

import jsonpickle

# new
class model(object):
	def toJson(self):
		return jsonpickle.encode(self)
	def fromJson(self,jsonstring):
		self = jsonpickle.decode(jsonstring)
		return self

class arch(model):

	id = None
	name = None

	def __init__(self,id,name):
		self.id = id
		self.name = name

class dist(model):

	id = None
	name = None

	def __init__(self,id,name):
		self.id = id
		self.name = name

class format(model):

	id = None
	name = None

	def __init__(self,id,name):
		self.id = id
		self.name = name

class status(model):

	id = None
	name = None

	def __init__(self,id,name):
		self.id = id
		self.name = name

class suite(model):

	id = None
	name = None

	def __init__(self,id,name):
		self.id = id
		self.name = name

class buildd(model):

	id = None
	name = None

	def __init__(self,id,name):
		self.id = id
		self.name = name

class job(model):

	id = None
	packageinstance = None
	buildclient_id = None

	def __init__(self,id,packageinstance,buildclient_id):
		self.id = id
		self.packageinstance = packageinstance
		self.buildclient_id = buildclient_id

class package(model):

	id = None
	version = None
	name = None

	def __init__(self,id,version,name):
		self.id = id
		self.version = version
		self.name = name

class packageinstance(model):

	id = None
	suite = None
	package = None
	version = None
	arch  = None
	format  = None
	distribution  = None

	def __init__(self, id, suite, package, version, arch, format, distribution) :
		self.id = id
		self.suite = suite
		self.version = version
		self.arch = arch
		self.format = format
		self.distribution = distribution
