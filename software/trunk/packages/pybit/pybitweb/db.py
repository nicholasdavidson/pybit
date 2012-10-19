#!/usr/bin/python

import psycopg2
import psycopg2.extras
import jsonpickle
from pybit.models import arch,dist,format,status,suite,buildd,job,package,packageinstance,suitearch

#TODO: make more robust, more DELETEs?

class db(object):

	conn = None
	cur = None
	
	#<<<<<<<< General database functions >>>>>>>>

	#Constructor, connects on initialisation. Do we need to make sure we dont make too many of these? (pooling?)

	def load_settings_from_file(self,path):
		settings_file = open(path, 'r')
		encoded_string = settings_file.read()
		settings = jsonpickle.decode(encoded_string )
		return settings

	def __init__(self):
		self.settings = self.load_settings_from_file('configs/db_settings.json')
		self.connect()

	#Deconstructor, disconnects on disposal. Need to check this actually gets called.
	def __del__(self):
		self.disconnect()

	#Connects to DB. Hardcoding the connection string in here is probably a bad idea...
	def connect(self):
		try:
			self.conn = psycopg2.connect(database=self.settings['database'], user=self.settings['user'], host=self.settings['host'], port=self.settings['port'])
			self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			return True
		except Exception as e:
			raise Exception('Error connecting to database:' + str(e))
			return False

	#When to call this? - Does python have deconstructors?
	def disconnect(self):
		try:
			self.conn.commit()
			self.cur.close()
			self.conn.close()
			return True
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error disconnecting from database:' + str(e))
			return False

	#<<<<<<<< Lookup table queries >>>>>>>>
	# Do we care about update or delete?

	def get_arches(self):
		try:
			self.cur.execute("SELECT id,name FROM arch ORDER BY name")
			res = self.cur.fetchall()
			self.conn.commit()

			arches = []
			for i in res:
				arches.append(arch(i['id'],i['name']))
			return arches
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving arches list:' + str(e))
			return None

	def get_arch_id(self,id):
		try:
			self.cur.execute("SELECT id,name FROM arch WHERE id=%s",(id,))
			res = self.cur.fetchall()
			self.conn.commit()

			return arch(res[0]['id'],res[0]['name'])
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving arch with id:' + id + str(e))
			return None

	def get_arch_byname(self,name):
		try:
			self.cur.execute("SELECT id,name FROM arch WHERE name=%s",(name,))
			res = self.cur.fetchall()
			self.conn.commit()

			arches = []
			for i in res:
				arches.append(arch(i['id'],i['name']))
			return arches
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving arch by name:' + name + str(e))
			return None

	def put_arch(self,name):
		try:
			self.cur.execute("INSERT into arch(name) VALUES (%s) RETURNING id",(name,))
			res = self.cur.fetchall()
			self.conn.commit()

			return arch(res[0]['id'],name)
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error adding arch:' + name + str(e))
			return None

	def get_suitearches(self):
		try:
			self.cur.execute("SELECT id,suite_id,arch_id FROM suitearches ORDER BY id")
			res = self.cur.fetchall()
			self.conn.commit()

			suitearches = []
			for i in res:
				suitearches.append(suitearch(i['id'],i['suite_id'],i['arch_id']))
			return suitearches
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving suite arches list:' + str(e))
			return None

	def get_suitearch_id(self,id):
		try:
			self.cur.execute("SELECT id,suite_id,arch_id FROM suitearches WHERE id=%s",(id,))
			res = self.cur.fetchall()
			self.conn.commit()

			return suitearch(res[0]['id'],res[0]['suite_id'],res[0]['arch_id'])
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving suite arch with id:' + id + str(e))
			return None

	def put_suitearch(self,suite_id,arch_id):
		try:
			self.cur.execute("INSERT into suitearches(suite_id,arch_id) VALUES (%s, %s) RETURNING id",(suite_id,arch_id))
			res = self.cur.fetchall()
			self.conn.commit()

			return suitearch(res[0]['id'],suite_id,arch_id)
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error adding suite arch:' + suite_id + arch_id + str(e))
			return None

	def get_dists(self):
		try:
			self.cur.execute("SELECT id,name FROM distribution ORDER BY name")
			res = self.cur.fetchall()
			self.conn.commit()

			dists = []
			for i in res:
				dists.append(dist(i['id'],i['name']))
			return dists
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving dist list:' + str(e))
			return None

	def get_dist_id(self,id):
		try:
			self.cur.execute("SELECT id,name FROM distribution WHERE id=%s",(id,))
			res = self.cur.fetchall()
			self.conn.commit()

			return dist(res[0]['id'],res[0]['name'])
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving dist with id:' + id + str(e))
			return None

	def get_dist_byname(self,name):
		try:
			self.cur.execute("SELECT id,name FROM distribution WHERE name=%s",(name,))
			res = self.cur.fetchall()
			self.conn.commit()

			dists = []
			for i in res:
				dists.append(dist(i['id'],i['name']))
			return dists
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving dist by name:' + name + str(e))
			return None

	def put_dist(self,name):
		try:
			self.cur.execute("INSERT into distribution(name) VALUES (%s)  RETURNING id",(name,))
			res = self.cur.fetchall()
			self.conn.commit()

			return dist(res[0]['id'],name)
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error adding dist:' + name + str(e))
			return None

	def get_formats(self):
		try:
			self.cur.execute("SELECT id,name FROM format ORDER BY name")
			res = self.cur.fetchall()
			self.conn.commit()

			formats = []
			for i in res:
				formats.append(format(i['id'],i['name']))
			return formats
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving formats list:' + str(e))
			return None

	def get_format_id(self,id):
		try:
			self.cur.execute("SELECT id,name FROM format WHERE id=%s",(id,))
			res = self.cur.fetchall()
			self.conn.commit()

			return format(res[0]['id'],res[0]['name'])
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving format with id:' + id + str(e))
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
			raise Exception('Error retrieving format by name:' + name + str(e))
			return None

	def put_format(self,name):
		try:
			self.cur.execute("INSERT into format(name) VALUES (%s)  RETURNING id",(name,))
			res = self.cur.fetchall()
			self.conn.commit()

			return format(res[0]['id'],name)
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error adding format:' + name + str(e))
			return None

	def get_statuses(self):
		try:
			self.cur.execute("SELECT id,name FROM status ORDER BY name")
			res = self.cur.fetchall()
			self.conn.commit()

			statuses = []
			for i in res:
				statuses.append(status(i['id'],i['name']))
			return statuses
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving status list:' + str(e))
			return None

	def get_status_id(self,id):
		try:
			self.cur.execute("SELECT id,name FROM status WHERE id=%s",(id,))
			res = self.cur.fetchall()
			self.conn.commit()

			return status(res[0]['id'],res[0]['name'])
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving status with id:' + id + str(e))
			return None

	def put_status(self,name):
		try:
			self.cur.execute("INSERT into status(name) VALUES (%s)  RETURNING id",(name,))
			res = self.cur.fetchall()
			self.conn.commit()

			return status(res[0]['id'],name)
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error add status:' + name + str(e))
			return None

	def get_suites(self):
		try:
			self.cur.execute("SELECT id,name FROM suite ORDER BY name")
			res = self.cur.fetchall()
			self.conn.commit()

			suites = []
			for i in res:
				suites.append(suite(i['id'],i['name']))
			return suites
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving suite list:' + str(e))
			return None

	def get_suite_id(self,id):
		try:
			self.cur.execute("SELECT id,name FROM suite WHERE id=%s",(id,))
			res = self.cur.fetchall()
			self.conn.commit()

			return suite(res[0]['id'],res[0]['name'])
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving suite with id:' + id + str(e))
			return None

	def get_suite_byname(self,name):
		try:
			self.cur.execute("SELECT id,name FROM suite WHERE name=%s",(name,))
			res = self.cur.fetchall()
			self.conn.commit()

			suites = []
			for i in res:
				suites.append(suite(i['id'],i['name']))
			return suites
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving suite with name:' + name + str(e))
			return None

	def put_suite(self,name):
		try:
			self.cur.execute("INSERT into suite(name) VALUES (%s)  RETURNING id",(name,))
			res = self.cur.fetchall()
			self.conn.commit()

			return suite(res[0]['id'],name)
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error adding suite:' + name + str(e))
			return None

	#<<<<<<<< BuildD related database functions >>>>>>>>

	def get_buildclients(self):
		try:
			self.cur.execute("SELECT id,name FROM buildclients ORDER BY name")
			res = self.cur.fetchall()
			self.conn.commit()

			buildds = []
			for i in res:
				buildds.append(buildd(i['id'],i['name']))
			return buildds
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving buildd list:' + str(e))
			return None

	def get_buildd_id(self,id):
		try:
			self.cur.execute("SELECT id,name FROM buildclients WHERE id=%s",(id,))
			res = self.cur.fetchall()
			self.conn.commit()

			return buildd(res[0]['id'],res[0]['name'])
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving buildd with id:' + id + str(e))
			return None

	def put_buildclient(self,name):
		try:
			self.cur.execute("INSERT into buildclients(name) VALUES (%s)  RETURNING id",(name,))
			res = self.cur.fetchall()
			self.conn.commit()

			return buildd(res[0]['id'],name)
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error adding buildd:' + name + str(e))
			return None

	def delete_buildclient(self,id):
		try:
			self.cur.execute("DELETE FROM buildclients WHERE id=%s RETURNING id",(id,))
			res = self.cur.fetchall() # TODO: check
			self.conn.commit()

			if res[0]['id'] == id:
				return True
			else:
				return False
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error deleting buildd with id:' + id + str(e))
			return None

	def get_buildd_jobs(self,id):
		try:
			self.cur.execute("SELECT job.id,buildclients.id FROM buildclients,job WHERE buildclients.id=%s AND buildclients.id = job.buildclient_id  ORDER BY job.id",(id,))
			res = self.cur.fetchall()
			self.conn.commit()

			return res
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving jobs on buildd with id:' + id + str(e))
			return None

	#<<<<<<<< Job related database functions >>>>>>>>
	# UPDATE queries?

	def get_job(self,id):
		try:
			self.cur.execute("SELECT id,packageinstance_id,buildclient_id FROM job WHERE id=%s",(id,))
			res = self.cur.fetchall()
			self.conn.commit()

			packageinstance = self.get_packageinstance_id(res[0]['packageinstance_id'])
			buildclient = self.get_buildd_id(res[0]['buildclient_id']) if res[0]['buildclient_id'] else None
			return job(res[0]['id'],packageinstance,buildclient)
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving job with id:' + id + str(e))
			return None

	def get_jobs(self):
		try:
			self.cur.execute("SELECT id,packageinstance_id,buildclient_id FROM job ORDER BY id")
			res = self.cur.fetchall()
			self.conn.commit()

			jobs = []
			for i in res:
				packageinstance = self.get_packageinstance_id(i['packageinstance_id'])
				buildclient = self.get_buildd_id(i['buildclient_id']) if i['buildclient_id'] else None 
				jobs.append(job(i['id'],packageinstance,buildclient))
			return jobs
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving jobs list:' + str(e))
			return None

	def get_jobs_by_status(self,status):
		try:
			self.cur.execute("WITH latest_status AS (SELECT DISTINCT ON (job_id) job_id, status.name FROM jobstatus LEFT JOIN status ON status_id=status.id ORDER BY job_id, time DESC) SELECT job_id, name FROM latest_status WHERE name=%s",(status,));
			res = self.cur.fetchall()
			self.conn.commit()

			jobs = []
			for i in res:
				jobs.append(self.get_job(i['job_id']))
			return jobs
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving jobs list with status:' + status + str(e))
			return None

	def get_unfinished_jobs(self):
		try:
			self.cur.execute("WITH latest_status AS (SELECT DISTINCT ON (job_id) job_id, status.name FROM jobstatus LEFT JOIN status ON status_id=status.id ORDER BY job_id, time DESC) SELECT job_id, name FROM latest_status WHERE name!='Uploaded' AND name!='Done'");
			res = self.cur.fetchall()
			self.conn.commit()

			jobs = []
			for i in res:
				jobs.append(self.get_job(i['job_id']))
			return jobs
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving unfinished jobs:' + str(e))
			return None

	def get_job_status(self,id):
		try:
			#TODO: CODEME - gets job status *history*

			jobstatus = []
			return jobstatus
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving job status with:' + id + str(e))
			return None

	def delete_job(self,id):
		try:
			self.cur.execute("DELETE FROM job WHERE id=%s  RETURNING id",(id,))
			res = self.cur.fetchall() # TODO: check
			self.conn.commit()
			if res[0]['id'] == id:
				return True
			else:
				return False
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error deleting job with:' + id + str(e))
			return None

	def put_job(self,packageinstance,buildclient):
		try:
			#TODO: work in progress
			self.cur.execute("INSERT INTO job (packageinstance_id,buildclient_id) VALUES (%s, %s)  RETURNING id",(packageinstance.id,(buildclient.id if buildclient else None)))
			res = self.cur.fetchall()
			self.conn.commit()

			return job(res[0]['id'],packageinstance,buildclient)
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error adding job:' + str(e))
			return None

	#<<<<<<<< Package related database functions >>>>>>>>
	# UPDATE queries?
	def get_packages(self):
		try:
			self.cur.execute("SELECT id,version,name FROM package ORDER BY name")
			res = self.cur.fetchall()
			self.conn.commit()

			packages = []
			for i in res:
				packages.append(package(i['id'],i['version'],i['name']))
			return packages
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving packages list:' + str(e))
			return None

	def get_package_id(self,id):
		try:
			self.cur.execute("SELECT id,version,name FROM package WHERE id=%s",(id,))
			res = self.cur.fetchall()
			self.conn.commit()

			return package(res[0]['id'],res[0]['version'],res[0]['name'])
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving package with id:' + id + str(e))
			return None

	def get_package_byvalues(self,name,version):
		try:
			self.cur.execute("SELECT id,name,version FROM package WHERE name=%s AND version=%s",(name,version))
			res = self.cur.fetchall()
			self.conn.commit()

			packages = []
			for i in res:
				packages.append(package(i['id'],i['version'],i['name']))
			return packages
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving package by values:' + name + version + str(e))
			return None

	def put_package(self,version,name):
		try:
			self.cur.execute("INSERT into package(version,name) VALUES (%s, %s)  RETURNING id",(version,name))
			res = self.cur.fetchall()
			self.conn.commit()

			return package(res[0]['id'],version,name)
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error adding package:' + name + version + str(e))
			return None

	def delete_package(self,id):
		try:
			self.cur.execute("DELETE FROM package WHERE id=%s  RETURNING id",(id,))
			res = self.cur.fetchall() # TODO: check
			self.conn.commit()

			if res[0]['id'] == id:
				return True
			else:
				return False
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error deleting package with:' + id + str(e))
			return None

	#<<<<<<<<< Packageinstance related Queries >>>>>>>
	# TODO: TEST
	def get_packageinstances(self):
		try:
			self.cur.execute("SELECT id,package_id,arch_id,suite_id,dist_id,format_id,master FROM packageinstance ORDER BY package_id, id")
			res = self.cur.fetchall()
			self.conn.commit()

			packageinstances = []
			for i in res:
				packageinstances.append(packageinstance(i['id'],i['package_id'],i['arch_id'],i['suite_id'],i['dist_id'],i['format_id'],i['master']))
			return packageinstances
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving package instances list:' + str(e))
			return None

	def get_packageinstance_byvalues(self,package_id,arch_id,suite_id,dist_id,format_id):
		try:
			self.cur.execute("SELECT id,package_id,arch_id,suite_id,dist_id,format_id,master FROM packageinstance WHERE package_id=%s AND arch_id=%s AND suite_id=%s AND dist_id=%s AND format_id=%s",(package_id,arch_id,suite_id,dist_id,format_id))
			res = self.cur.fetchall()
			self.conn.commit()

			packageinstances = []
			for i in res:
				packageinstances.append(packageinstance(i['id'],i['package_id'],i['arch_id'],i['suite_id'],i['dist_id'],i['format_id'],i['master']))
			return packageinstances
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving package instance by value:' + str(e))
			return None

	def get_packageinstance_id(self,id):
		try:
			self.cur.execute("SELECT id,package_id,arch_id,suite_id,dist_id,format_id,master FROM packageinstance  WHERE id=%s",(id,))
			res = self.cur.fetchall()
			self.conn.commit()

			package = self.get_package_id(res[0]['package_id'])
			arch = self.get_arch_id(res[0]['arch_id'])
			suite = self.get_suite_id(res[0]['suite_id'])
			dist = self.get_dist_id(res[0]['dist_id'])
			format = self.get_format_id(res[0]['format_id'])
			return packageinstance(res[0]['id'],package,arch,suite,dist,format,res[0]['master'])
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving package instance with:' + id + str(e))
			return None

	def put_packageinstance(self,package,arch,suite,dist,format,master):
		try:
			self.cur.execute("INSERT into packageinstance(package_id,arch_id,suite_id,dist_id,format_id,master) VALUES (%s, %s, %s, %s, %s, %s)  RETURNING id",(package.id,arch.id,suite.id,dist.id,format.id,master))
			self.conn.commit()
			res = self.cur.fetchall()
			self.conn.commit()

			return packageinstance(res[0]['id'],package,arch,suite,dist,format,master)
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error adding package instance:' + package + arch + suite + dist + format + master + str(e))
			return None

	def delete_packageinstance(self,id):
		try:
			self.cur.execute("DELETE FROM packageinstance WHERE id=%s RETURNING id",(id,))
			res = self.cur.fetchall() # TODO: check
			self.conn.commit()

			if res[0]['id'] == id:
				return True
			else:
				return False
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error deleting package instance with:' + id + str(e))
			return None

	# <<<<< TODO: This is a work in progress!!! >>>>>
	def check_specific_packageinstance_exists(self,arch,package,distribution,format,suite):
		try:
			if arch and distribution and format and package and suite:
				self.cur.execute("SELECT id FROM packageinstance WHERE arch_id=%s AND dist_id=%s AND format_id=%s AND package_id=%s AND suite_id=%s",(arch.id,distribution.id,format.id,package.id,suite.id))
				res = self.cur.fetchall()
				self.conn.commit()

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
			self.conn.rollback()
			raise Exception('Error checking package instance exists:' + str(e))
			return None
	#<<<<<<<<< Report Queries >>>>>>>

	def get_report_package_instance(self):
		try:
			self.cur.execute("SELECT packageinstance.id, suite.name AS suite, package.name AS package, package.version AS version, arch.name AS arch, format.name AS format, distribution.name AS dist, packageinstance.master AS master FROM packageinstance LEFT JOIN arch ON arch.id=arch_id LEFT JOIN suite ON suite.id=suite_id LEFT JOIN distribution ON distribution.id=dist_id LEFT JOIN package ON package_id=package.id LEFT JOIN format ON format_id=format.id")
			res = self.cur.fetchall()
			self.conn.commit()

			package_instances = []
			for i in res :
				package_instances.append(packageinstance(i['id'], i['package'], i['arch'], i['suite'], i['dist'], i['format'], i['master']))
			return package_instances
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving package instance list:' + str(e))
			return None

	def supportedArchitectures(self,suite) :
		try:
			if suite :
				self.cur.execute("SELECT arch.id, arch.name FROM suite LEFT JOIN suitearches ON suite.id=suite_id LEFT JOIN arch ON arch_id = arch.id WHERE suite.name=%s",[suite])
				res = self.cur.fetchall()
				self.conn.commit()

				arch_list = []
				for i in res :
					arch_list.append(i['name'])
				return arch_list
			else:
				return False
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving supported architectures for:' + suite + str(e))
			return None
