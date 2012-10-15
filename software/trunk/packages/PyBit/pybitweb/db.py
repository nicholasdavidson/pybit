#!/usr/bin/python

import psycopg2
import psycopg2.extras
from models import arch,dist,format,status,suite,buildd,job,package,packageinstance

#TODO: make more robust, more DELETEs?

class db:

	conn = None
	cur = None

	#<<<<<<<< General database functions >>>>>>>>

	#Constructor, connects on initialisation. Do we need to make sure we dont make too many of these? (pooling?)
	def __init__(self):
		self.connect()

	#Deconstructor, disconnects on disposal. Need to check this actually gets called.
	def __del__(self):
		self.disconnect()

	#Connects to DB. Hardcoding the connection string in here is probably a bad idea...
	def connect(self):
		try:
			self.conn = psycopg2.connect(database="pybit", user="postgres", host="catbells", port="5432")
			self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
		except Exception as e:
			raise Exception('Error connecting to database: ' + str(e))
			return None

	#When to call this? - Does python have deconstructors?
	def disconnect(self):
		try:
			self.conn.commit()
			self.cur.close()
			self.conn.close()
		except Exception as e:
			raise Exception('Error disconnecting from database: ' + str(e))
			return None

	#<<<<<<<< Lookup table queries >>>>>>>>
	# Do we care about update or delete?

	def get_arches(self):
		try:
			self.cur.execute("SELECT id,name FROM arch ORDER BY name")
			res = self.cur.fetchall()

			arches = []
			for i in res:
				arches.append(arch(i['id'],i['name']))
			return arches
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def get_arch_id(self,id):
		try:
			self.cur.execute("SELECT id,name FROM arch WHERE id=%s",(id,))
			res = self.cur.fetchall()

			arches = []
			for i in res:
				arches.append(arch(i['id'],i['name']))
			return arches
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def get_arch_byname(self,name):
		try:
			self.cur.execute("SELECT id,name FROM arch WHERE name=%s",(name,))
			res = self.cur.fetchall()

			arches = []
			for i in res:
				arches.append(arch(i['id'],i['name']))
			return arches
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def put_arch(self,name):
		try:
			self.cur.execute("INSERT into arch(name) VALUES (%s) RETURNING id",(name,))
			self.conn.commit()
			res = self.cur.fetchall()
			tmp = arch(res[0]['id'],name)
			return tmp
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def get_dists(self):
		try:
			self.cur.execute("SELECT id,name FROM distribution ORDER BY name")
			res = self.cur.fetchall()

			dists = []
			for i in res:
				dists.append(dist(i['id'],i['name']))
			return dists
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def get_dist_id(self,id):
		try:
			self.cur.execute("SELECT id,name FROM distribution WHERE id=%s",(id,))
			res = self.cur.fetchall()

			dists = []
			for i in res:
				dists.append(dist(i['id'],i['name']))
			return dists
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def get_dist_byname(self,name):
		try:
			self.cur.execute("SELECT id,name FROM distribution WHERE name=%s",(name,))
			res = self.cur.fetchall()

			dists = []
			for i in res:
				dists.append(dist(i['id'],i['name']))
			return dists
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def put_dist(self,name):
		try:
			self.cur.execute("INSERT into distribution(name) VALUES (%s)  RETURNING id",(name,))
			self.conn.commit()
			res = self.cur.fetchall()
			tmp = dist(res[0]['id'],name)
			return tmp
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def get_formats(self):
		try:
			self.cur.execute("SELECT id,name FROM format ORDER BY name")
			res = self.cur.fetchall()

			formats = []
			for i in res:
				formats.append(format(i['id'],i['name']))
			return formats
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def get_format_id(self,id):
		try:
			self.cur.execute("SELECT id,name FROM format WHERE id=%s",(id,))
			res = self.cur.fetchall()

			formats = []
			for i in res:
				formats.append(format(i['id'],i['name']))
			return formats
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def get_format_byname(self,name):
		try:
			self.cur.execute("SELECT id,name FROM format WHERE name=%s",(name,))
			res = self.cur.fetchall()

			formats = []
			for i in res:
				formats.append(format(i['id'],i['name']))
			return formats
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def put_format(self,name):
		try:
			self.cur.execute("INSERT into format(name) VALUES (%s)  RETURNING id",(name,))
			self.conn.commit()
			res = self.cur.fetchall()
			tmp = format(res[0]['id'],name)
			return tmp
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def get_statuses(self):
		try:
			self.cur.execute("SELECT id,name FROM status ORDER BY name")
			res = self.cur.fetchall()

			statuses = []
			for i in res:
				statuses.append(status(i['id'],i['name']))
			return statuses
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def get_status_id(self,id):
		try:
			self.cur.execute("SELECT id,name FROM status WHERE id=%s",(id,))
			res = self.cur.fetchall()

			statuses = []
			for i in res:
				statuses.append(status(i['id'],i['name']))
			return statuses
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def put_status(self,name):
		try:
			self.cur.execute("INSERT into status(name) VALUES (%s)  RETURNING id",(name,))
			self.conn.commit()
			res = self.cur.fetchall()
			tmp = status(res[0]['id'],name)
			return tmp
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def get_suites(self):
		try:
			self.cur.execute("SELECT id,name FROM suite ORDER BY name")
			res = self.cur.fetchall()

			suites = []
			for i in res:
				suites.append(suite(i['id'],i['name']))
			return suites
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def get_suite_id(self,id):
		try:
			self.cur.execute("SELECT id,name FROM suite WHERE id=%s",(id,))
			res = self.cur.fetchall()

			suites = []
			for i in res:
				suites.append(suite(i['id'],i['name']))
			return suites
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def get_suite_byname(self,name):
		try:
			self.cur.execute("SELECT id,name FROM suite WHERE name=%s",(name,))
			res = self.cur.fetchall()

			suites = []
			for i in res:
				suites.append(suite(i['id'],i['name']))
			return suites
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def put_suite(self,name):
		try:
			self.cur.execute("INSERT into suite(name) VALUES (%s)  RETURNING id",(name,))
			self.conn.commit()
			res = self.cur.fetchall()
			tmp = suite(res[0]['id'],name)
			return tmp
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	#<<<<<<<< BuildD related database functions >>>>>>>>

	def get_buildclients(self):
		try:
			self.cur.execute("SELECT id,name FROM buildclients ORDER BY name")
			res = self.cur.fetchall()

			buildds = []
			for i in res:
				buildds.append(buildd(i['id'],i['name']))
			return buildds
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def get_buildd_id(self,id):
		try:
			self.cur.execute("SELECT id,name FROM buildclients WHERE id=%s",(id,))
			res = self.cur.fetchall()

			buildds = []
			for i in res:
				buildds.append(buildd(i['id'],i['name']))
			return buildds
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def put_buildclient(self,name):
		try:
			self.cur.execute("INSERT into buildclients(name) VALUES (%s)  RETURNING id",(name,))
			self.conn.commit()
			res = self.cur.fetchall()
			tmp = buildd(res[0]['id'],name)
			return tmp
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def delete_buildclient(self,id):
		try:
			self.cur.execute("DELETE FROM buildclients WHERE id=%s RETURNING id",(id,))
			self.conn.commit()
			res = self.cur.fetchall() # TODO: check

			if res[0]['id'] == id:
				return True
			else:
				return False
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def get_buildd_jobs(self,id):
		try:
			self.cur.execute("SELECT job.id,buildclients.id FROM buildclients,job WHERE buildclients.id=%s AND buildclients.id = job.buildclient_id  ORDER BY job.id",(id,))
			res = self.cur.fetchall()
			return res
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	#<<<<<<<< Job related database functions >>>>>>>>
	# UPDATE queries?

	def get_jobs(self):
		try:
			self.cur.execute("SELECT id,packageinstance_id,buildclient_id FROM job ORDER BY id")
			res = self.cur.fetchall()

			jobs = []
			for i in res:
				jobs.append(job(i['id'],i['packageinstance_id'],i['buildclient_id']))
			return jobs
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def get_job(self,id):
		try:
			self.cur.execute("SELECT id,packageinstance_id,buildclient_id FROM job WHERE id=%s",(id,))
			res = self.cur.fetchall()

			jobs = []
			for i in res:
				jobs.append(job(i['id'],i['packageinstance_id'],i['buildclient_id']))
			return jobs
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def get_job_status(self,id):
		try:
			#TODO: work in progress
			self.cur.execute("SELECT job.id, status.name FROM job, jobstatus, status WHERE job.id=%s AND job.id = jobstatus.job_id AND job.status_id = status.id",(id,))
			res = self.cur.fetchall()
			return res
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def delete_job(self,id):
		try:
			self.cur.execute("DELETE FROM job WHERE id=%s  RETURNING id",(id,))
			self.conn.commit()
			res = self.cur.fetchall() # TODO: check
			if res[0]['id'] == id:
				return True
			else:
				return False
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def put_job(self,packageinstance_id,buildclient_id):
		try:
			#TODO: work in progress
			self.cur.execute("INSERT INTO job (packageinstance_id,buildclient_id) VALUES (%s, %s)  RETURNING id",(packageinstance_id,buildclient_id))
			self.conn.commit()
			res = self.cur.fetchall()
			tmp = job(res[0]['id'],packageinstance_id,buildclient_id)
			return tmp
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	#<<<<<<<< Package related database functions >>>>>>>>
	# UPDATE queries?
	def get_packages(self):
		try:
			self.cur.execute("SELECT id,version,name FROM package ORDER BY name")
			res = self.cur.fetchall()

			packages = []
			for i in res:
				packages.append(package(i['id'],i['version'],i['name']))
			return packages
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def get_package_id(self,id):
		try:
			self.cur.execute("SELECT id,version,name FROM package WHERE id=%s",(id,))
			res = self.cur.fetchall()

			packages = []
			for i in res:
				packages.append(package(i['id'],i['version'],i['name']))
			return packages
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def get_package_byvalues(self,name,version):
		try:
			self.cur.execute("SELECT id,name,version FROM package WHERE name=%s AND version=%s",(name,version))
			res = self.cur.fetchall()

			packages = []
			for i in res:
				packages.append(package(i['id'],i['version'],i['name']))
			return packages
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def put_package(self,version,name):
		try:
			self.cur.execute("INSERT into package(version,name) VALUES (%s, %s)  RETURNING id",(version,name))
			self.conn.commit()
			res = self.cur.fetchall()
			tmp = package(res[0]['id'],version,name)
			return tmp
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def delete_package(self,id):
		try:
			self.cur.execute("DELETE FROM package WHERE id=%s  RETURNING id",(id,))
			self.conn.commit()
			res = self.cur.fetchall() # TODO: check
			if res[0]['id'] == id:
				return True
			else:
				return False
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	#<<<<<<<<< Packageinstance related Queries >>>>>>>
	# TODO: TEST
	def get_packageinstances(self):
		try:
			self.cur.execute("SELECT id,package_id,arch_id,suite_id,dist_id,format_id,master FROM packageinstance ORDER BY package_id, id")
			res = self.cur.fetchall()

			packageinstances = []
			for i in res:
				packageinstances.append(packageinstance(i['id'],i['package_id'],i['arch_id'],i['suite_id'],i['dist_id'],i['format_id'],i['master']))
			return packageinstances
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def get_packageinstance_byvalues(self,package_id,arch_id,suite_id,dist_id,format_id):
		try:
			self.cur.execute("SELECT id,package_id,arch_id,suite_id,dist_id,format_id,master FROM packageinstance WHERE package_id=%s AND arch_id=%s AND suite_id=%s AND dist_id=%s AND format_id=%s",(package_id,arch_id,suite_id,dist_id,format_id))
			res = self.cur.fetchall()

			packageinstances = []
			for i in res:
				packageinstances.append(packageinstance(i['id'],i['package_id'],i['arch_id'],i['suite_id'],i['dist_id'],i['format_id'],i['master']))
			return packageinstances
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def get_packageinstance_id(self,id):
		try:
			self.cur.execute("SELECT id,package_id,arch_id,suite_id,dist_id,format_id,master FROM packageinstance  WHERE id=%s",(id,))
			res = self.cur.fetchall()

			packageinstances = []
			for i in res:
				packageinstances.append(packageinstance(i['id'],i['package_id'],i['arch_id'],i['suite_id'],i['dist_id'],i['format_id'],i['master']))
			return packageinstances
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def put_packageinstance(self,package_id,arch_id,suite_id,dist_id,format_id,master):
		try:
			self.cur.execute("INSERT into packageinstance(package_id,arch_id,suite_id,dist_id,format_id,master) VALUES (%s, %s, %s, %s, %s, %s)  RETURNING id",(package_id,arch_id,suite_id,dist_id,format_id,master))
			self.conn.commit()
			res = self.cur.fetchall()
			tmp = packageinstance(res[0]['id'],package_id,arch_id,suite_id,dist_id,format_id,master)
			return tmp
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def delete_packageinstance(self,id):
		try:
			self.cur.execute("DELETE FROM packageinstance WHERE id=%s RETURNING id",(id,))
			self.conn.commit()
			res = self.cur.fetchall() # TODO: check
			if res[0]['id'] == id:
				return True
			else:
				return False
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	# <<<<< TODO: This is a work in progress!!! >>>>>
	def check_specific_packageinstance_exists(self,arch,distribution,format,packagename,packageversion,suite):
		try:
			if arch and distribution and format and packagename and packageversion and suite:
				archidID =  self.get_arch_byname(arch)
				distributionID = self.get_dist_byname(distribution)
				formatID =  self.get_format_byname(format)
				packageID =  self.get_package_byvalues(packagename,packageversion)
				suiteID = self.get_suite_byname(suite)
			else:
				#Error finding specific package instance
				return False

			if archidID and distributionID and formatID and packageID and suiteID:
				self.cur.execute("SELECT id FROM packageinstance WHERE arch_id=%s AND dist_id=%s AND format_id=%s AND package_id=%s AND suite_id=%s",(archidID[0].id,distributionID[0].id,formatID[0].id,packageID[0].id,suiteID[0].id))
				res = self.cur.fetchall()
				if len(res) > 0:
					#Found specific package instance
					return True
				else:
					# doesnt exist
					#Cannot find specific package instance
					return False
			else:
				#Error finding specific package instance
				return False
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None
	#<<<<<<<<< Report Queries >>>>>>>

	def get_report_package_instance(self):
		try:
			self.cur.execute("SELECT packageinstance.id, suite.name AS suite, package.name AS package, package.version AS version, arch.name AS arch, format.name AS format, distribution.name AS dist, packageinstance.master AS master FROM packageinstance LEFT JOIN arch ON arch.id=arch_id LEFT JOIN suite ON suite.id=suite_id LEFT JOIN distribution ON distribution.id=dist_id LEFT JOIN package ON package_id=package.id LEFT JOIN format ON format_id=format.id")
			res = self.cur.fetchall()

			package_instances = []
			for i in res :
				package_instances.append(packageinstance(i['id'], i['package'], i['arch'], i['suite'], i['dist'], i['format'], i['master']))
			return package_instances
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None

	def supportedArchitectures(self,suite) :
		print "Suite: " + suite
		try:
			if suite :
				self.cur.execute("SELECT arch.id, arch.name FROM suite LEFT JOIN suitearches ON suite.id=suite_id LEFT JOIN arch ON arch_id = arch.id WHERE suite.name=%s",[suite])
				res = self.cur.fetchall()
				arch_list = []
				for i in res :
					arch_list.append(i['name'])
				return arch_list
			else:
				return False
		except Exception as e:
			raise Exception('Error performing database operation: ' + str(e))
			return None
