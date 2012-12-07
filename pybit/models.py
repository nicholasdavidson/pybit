import jsonpickle
import time

#       Copyright 2012:
#
#       Nick Davidson <nickd@toby-churchill.com>,
#       Simon Haswell <simonh@toby-churchill.com>,
#       Neil Williams <neilw@toby-churchill.com>,
#       James Bennet <github@james-bennet.com / James.Bennet@toby-churchill.com>

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

# TODO: Change DB methods and associated HTTP GEThandlers to work on these JSON objects, rather than returning the raw resultsets
# themselves, which are a pain to deserialise.

# new
class Model(object):
	def toJson(self):
		try:
			return jsonpickle.encode(self)
		except Exception as e:
			raise Exception('Error in toJson(): ' + str(e))
			return None
	def fromJson(self,jsonstring):
		try:
			self = jsonpickle.decode(jsonstring)
			return self
		except Exception as e:
			raise Exception('Error in fromJson(): ' + str(e))
			return None

class JobHistory(Model):
	def __init__(self,job_id,status,buildclient,time):
		self.job_id = job_id
		self.status = status
		self.buildclient = buildclient
		self.time = str(time) #????

class ClientMessage:
	failed = "Failed"
	building = "Building"
	done = "Done"
	blocked = "Blocked"
	waiting = "Waiting"
	cancelled = "Cancelled"

class Arch(Model):
	def __init__(self,arch_id,name):
		self.id = arch_id
		self.name = name

class Dist(Model):
	def __init__(self,dist_id,name):
		self.id = dist_id
		self.name = name

class Format(Model):
	def __init__(self,format_id,name):
		self.id = format_id
		self.name = name

class Status(Model):
	def __init__(self,status_id,name):
		self.id = status_id
		self.name = name

class Suite(Model):
	def __init__(self,suite_id,name):
		self.id = suite_id
		self.name = name

class BuildD(Model):
	def __init__(self,buildd_id,name):
		self.id = buildd_id
		self.name = name

class Package(Model):
	def __init__(self,package_id,version,name):
		self.id = package_id
		self.version = version
		self.name = name

class Transport(Model) :
	def __init__(self,transport_id,method,uri,vcs_id):
		self.id = transport_id
		self.method = method
		self.uri = uri
		self.vcs_id = vcs_id

class PackageInstance(Model):
	def __init__(self, packageinstance_id, package, arch, suite, distribution, pkg_format, master) :
		self.id = packageinstance_id
		self.package = package
		self.arch = arch
		self.suite = suite
		self.distribution = distribution
		self.format = pkg_format
		self.master = master


class Job(Model):
	def __init__(self,job_id,packageinstance,buildclient):
		self.id = job_id
		self.packageinstance = packageinstance
		self.buildclient = buildclient


class SuiteArch(Model):
	def __init__(self,suitearch_id,suite,arch,master_weight=0):
		self.id = suitearch_id
		self.suite = suite
		self.arch = arch
		self.master_weight = master_weight

class BuildRequest(Model):
	def __init__(self,job,transport,web_host,commands = None):
		self.job = job
		self.transport = transport
		self.web_host = web_host
		self.commands = commands # NEW: Any additional build commands
		self.timestamp = None

	def stamp_request (self) :
		self.timestamp = int(time.time())

	def get_buildstamp (self) :
		return self.timestamp

	def get_suite(self):
		return self.job.packageinstance.suite.name

	def get_package(self):
		return self.job.packageinstance.package.name

	def get_version(self):
		return self.job.packageinstance.package.version

	def get_arch(self):
		return self.job.packageinstance.arch.name

	def get_job_id(self):
		return self.job.id

	def get_dist(self):
		return self.job.packageinstance.distribution.name

	def get_format(self):
		return self.job.packageinstance.format.name


class AMQPConnection(object):
	def __init__(self, client_name, host, userid, password, vhost, insist=False):
		self.client_name = client_name
		self.host = host
		self.userid = userid
		self.password = password
		self.vhost = vhost
		self.insist = insist
	def as_dict(self):
		return  dict( host=self.host, userid=self.userid, password=self.password,
			virtual_host=self.vhost, insist= False )
	def __repr__(self):
		return "host: %s user id:%s password:%s vhost:%s insist: %s" % (
			self.host, self.userid, self.password, self.vhost, self.insist)



class CommandRequest(Model):
	def __init__(self,job,web_host):
		self.job = job
		self.web_host = web_host
	def get_job_id(self):
		return self.job.id

class CancelRequest(CommandRequest):
	def  __init__(self,job,web_host):
		CommandRequest.__init__(self, job, web_host)

class StatusRequest(CommandRequest):
	def  __init__(self,job,web_host):
		CommandRequest.__init__(self, job, web_host)

class TaskComplete(Model):
	def __init__(self, message, success = True):
		self.success = success
		self.message = message

def checkValue(value,container):
	if value in container and container[value] is not None and container[value] is not "":
		return True
	else:
		return False

