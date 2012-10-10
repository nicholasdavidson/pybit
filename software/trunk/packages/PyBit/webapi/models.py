#!/usr/bin/python

# TODO: Change DB methods and associated HTTP  GEThandlers to work on these JSON objects, rather than returning the raw resultsets themselves, which are a pain to deserialise.

class arch(object):
	
	id = None
	name = None
	
	def __init__(self,id,name):
		self.id = id
		self.name = name

class dist(object):
	
	id = None
	name = None
	
	def __init__(self,id,name):
		self.id = id
		self.name = name

class format(object):
	
	id = None
	name = None
	
	def __init__(self,id,name):
		self.id = id
		self.name = name

class status(object):
	
	id = None
	name = None
	
	def __init__(self,id,name):
		self.id = id
		self.name = name

class suite(object):
	
	id = None
	name = None
	
	def __init__(self,id,name):
		self.id = id
		self.name = name

class buildd(object):
	
	id = None
	name = None
	
	def __init__(self,id,name):
		self.id = id
		self.name = name

class job(object):
	
	id = None
	packageinstance = None
	buildclient_id = None
	
	def __init__(self,id,packageinstance,buildclient_id):
		self.id = id
		self.packageinstance = packageinstance
		self.buildclient_id = buildclient_id

class package(object):
	
	id = None
	version = None
	name = None
	
	def __init__(self,id,version,name):
		self.id = id
		self.version = version
		self.name = name
		
class packageinstance(object):
	
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
	
