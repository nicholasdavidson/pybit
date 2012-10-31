#!/usr/bin/python

import psycopg2
import psycopg2.extras
import jsonpickle
from pybit.models import Arch,Dist,Format,Status,Suite,BuildD,Job,Package,PackageInstance,SuiteArch,JobHistory
from pybit.common import load_settings_from_file

myDb = None

class Database(object):

	conn = None
	cur = None

	#<<<<<<<< General database functions >>>>>>>>

	#Constructor, connects on initialisation.

	def __init__(self):
		print "DEBUG: DB constructor called."
		if not myDb: # DONT allow construction of more than 1 db instance (i.e. none other than the myDb here)
			print "DEBUG: DB Singleton constructor called."
			self.settings = load_settings_from_file('db_settings.json')
			self.connect()

	#Deconstructor, disconnects on disposal.
	def __del__(self):
		self.disconnect()

	#Connects to DB using settings loaded from file.
	def connect(self):
		try:
			self.conn = psycopg2.connect(database=self.settings['db_databasename'], user=self.settings['db_user'], host=self.settings['db_hostname'], port=self.settings['db_port'])
			self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			return True
		except Exception as e:
			raise Exception('Error connecting to database:' + str(e))
			return False

	#Called by deconstructor
	def disconnect(self):
		try:
			if self.conn and self.cur:
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
				arches.append(Arch(i['id'],i['name']))
			return arches
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving arches list:' + str(e))
			return None

	def get_arch_id(self,arch_id):
		try:
			self.cur.execute("SELECT id,name FROM arch WHERE id=%s",(arch_id,))
			res = self.cur.fetchall()
			self.conn.commit()

			return Arch(res[0]['id'],res[0]['name'])
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving arch with id:' + str(arch_id) + str(e))
			return None

	# TODO: return single instance instead of list?
	def get_arch_byname(self,name):
		try:
			self.cur.execute("SELECT id,name FROM arch WHERE name=%s",(name,))
			res = self.cur.fetchall()
			self.conn.commit()

			arches = []
			for i in res:
				arches.append(Arch(i['id'],i['name']))
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

			return Arch(res[0]['id'],name)
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error adding arch:' + name + str(e))
			return None

	def get_suitearches(self):
		try:
			self.cur.execute("SELECT id,suite_id,arch_id FROM suitearches ORDER BY id")
			res = self.cur.fetchall()
			self.conn.commit()

			suite_arches = []
			for i in res:
				suite_arches.append(SuiteArch(i['id'],i['suite_id'],i['arch_id']))
			return suite_arches
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving suite arches list:' + str(e))
			return None

	def get_suitearch_id(self,suitearch_id):
		try:
			self.cur.execute("SELECT id,suite_id,arch_id FROM suitearches WHERE id=%s",(suitearch_id,))
			res = self.cur.fetchall()
			self.conn.commit()

			return SuiteArch(res[0]['id'],res[0]['suite_id'],res[0]['arch_id'])
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving suite arch with id:' + str(suitearch_id) + str(e))
			return None

	def put_suitearch(self,suite_id,arch_id):
		try:
			self.cur.execute("INSERT into suitearches(suite_id,arch_id) VALUES (%s, %s) RETURNING id",(suite_id,arch_id))
			res = self.cur.fetchall()
			self.conn.commit()

			return SuiteArch(res[0]['id'],suite_id,arch_id)
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
				dists.append(Dist(i['id'],i['name']))
			return dists
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving dist list:' + str(e))
			return None

	def get_dist_id(self,dist_id):
		try:
			self.cur.execute("SELECT id,name FROM distribution WHERE id=%s",(dist_id,))
			res = self.cur.fetchall()
			self.conn.commit()

			return Dist(res[0]['id'],res[0]['name'])
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving dist with id:' + str(dist_id) + str(e))
			return None

	# TODO: return single instance instead of list?
	def get_dist_byname(self,name):
		try:
			self.cur.execute("SELECT id,name FROM distribution WHERE name=%s",(name,))
			res = self.cur.fetchall()
			self.conn.commit()

			dists = []
			for i in res:
				dists.append(Dist(i['id'],i['name']))
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

			return Dist(res[0]['id'],name)
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
				formats.append(Format(i['id'],i['name']))
			return formats
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving formats list:' + str(e))
			return None

	def get_format_id(self,format_id):
		try:
			self.cur.execute("SELECT id,name FROM format WHERE id=%s",(format_id,))
			res = self.cur.fetchall()
			self.conn.commit()

			return Format(res[0]['id'],res[0]['name'])
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving format with id:' + str(format_id) + str(e))
			return None

	# TODO: return single instance instead of list?
	def get_format_byname(self,name):
		try:
			self.cur.execute("SELECT id,name FROM format WHERE name=%s",(name,))
			res = self.cur.fetchall()

			formats = []
			for i in res:
				formats.append(Format(i['id'],i['name']))
			return formats
		except Exception as e:
			raise Exception('Error retrieving format by name:' + name + str(e))
			return None

	def put_format(self,name):
		try:
			self.cur.execute("INSERT into format(name) VALUES (%s)  RETURNING id",(name,))
			res = self.cur.fetchall()
			self.conn.commit()

			return Format(res[0]['id'],name)
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
				statuses.append(Status(i['id'],i['name']))
			return statuses
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving status list:' + str(e))
			return None

	def get_status_id(self,status_id):
		try:
			self.cur.execute("SELECT id,name FROM status WHERE id=%s",(status_id,))
			res = self.cur.fetchall()
			self.conn.commit()

			return Status(res[0]['id'],res[0]['name'])
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving status with id:' + str(status_id) + str(e))
			return None

	def put_status(self,name):
		try:
			self.cur.execute("INSERT into status(name) VALUES (%s)  RETURNING id",(name,))
			res = self.cur.fetchall()
			self.conn.commit()

			return Status(res[0]['id'],name)
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
				suites.append(Suite(i['id'],i['name']))
			return suites
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving suite list:' + str(e))
			return None

	def get_suite_id(self,suite_id):
		try:
			self.cur.execute("SELECT id,name FROM suite WHERE id=%s",(suite_id,))
			res = self.cur.fetchall()
			self.conn.commit()

			return Suite(res[0]['id'],res[0]['name'])
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving suite with id:' + str(suite_id) + str(e))
			return None

	# TODO: return single instance instead of list?
	def get_suite_byname(self,name):
		try:
			self.cur.execute("SELECT id,name FROM suite WHERE name=%s",(name,))
			res = self.cur.fetchall()
			self.conn.commit()

			suites = []
			for i in res:
				suites.append(Suite(i['id'],i['name']))
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

			return Suite(res[0]['id'],name)
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

			build_clients = []
			for i in res:
				build_clients.append(BuildD(i['id'],i['name']))
			return build_clients
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving buildd list:' + str(e))
			return None

	def get_buildd_id(self,buildd_id):
		try:
			self.cur.execute("SELECT id,name FROM buildclients WHERE id=%s",(buildd_id,))
			res = self.cur.fetchall()
			self.conn.commit()

			return BuildD(res[0]['id'],res[0]['name'])
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving buildd with id:' + str(buildd_id) + str(e))
			return None

	def put_buildclient(self,name):
		try:
			self.cur.execute("INSERT into buildclients(name) VALUES (%s)  RETURNING id",(name,))
			res = self.cur.fetchall()
			self.conn.commit()

			return BuildD(res[0]['id'],name)
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error adding buildd:' + name + str(e))
			return None

	def delete_buildclient(self,buildclient_id):
		try:
			self.cur.execute("DELETE FROM buildclients WHERE id=%s RETURNING id",(buildclient_id,))
			res = self.cur.fetchall()
			self.conn.commit()

			if res[0]['id'] == buildclient_id:
				return True
			else:
				return False
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error deleting buildd with id:' + str(buildclient_id) + str(e))
			return None

	def get_buildd_jobs(self,buildclient_id):
		try:
			self.cur.execute("SELECT job.id AS job_id,packageinstance_id,buildclients.id AS buildclients_id FROM buildclients,job WHERE buildclients.id=%s AND buildclients.id = job.buildclient_id  ORDER BY job.id",(buildclient_id,))
			res = self.cur.fetchall()
			self.conn.commit()

			jobs = []
			for i in res:
				packageinstance = self.get_packageinstance_id(i['packageinstance_id'])
				jobs.append(jobs.append(Job(i['job_id'],packageinstance,buildclient_id)))

			return jobs
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving jobs on buildd with id:' + str(buildclient_id) + str(e))
			return None

	#<<<<<<<< Job related database functions >>>>>>>>
	# UPDATE queries?

	def get_job(self,job_id):
		try:
			self.cur.execute("SELECT id,packageinstance_id,buildclient_id FROM job WHERE id=%s",(job_id,))
			res = self.cur.fetchall()
			self.conn.commit()

			packageinstance = self.get_packageinstance_id(res[0]['packageinstance_id'])
			buildclient = self.get_buildd_id(res[0]['buildclient_id']) if res[0]['buildclient_id'] else None
			return Job(res[0]['id'],packageinstance,buildclient)
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving job with id:' + str(job_id) + str(e))
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
				jobs.append(Job(i['id'],packageinstance,buildclient))
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

	# TODO!!!!! - Testme
	def get_job_statuses(self,job_id):
	#gets job status *history*
		try:
			self.cur.execute("SELECT job.id AS job_id, status.name AS status, buildclients.name AS buildclient, jobstatus.time AS time FROM job LEFT JOIN jobstatus ON job.id=jobstatus.job_id LEFT JOIN status ON jobstatus.status_id=status.id  LEFT JOIN buildclients ON buildclients.id=job.buildclient_id WHERE job.id = %s ORDER BY time",(job_id,));
			res = self.cur.fetchall()
			self.conn.commit()
			jobstatuses = []
			for i in res:
				jobstatuses.append(JobHistory(i['job_id'],i['status'],i['buildclient'],i['time']))
			return jobstatuses
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving job status with:' + str(job_id) + str(e))
			return None

	def put_job_status(self, jobid, status):
		try:
			self.cur.execute("INSERT INTO jobstatus (job_id, status_id) VALUES (%s, (SELECT id FROM status WHERE name=%s)) ",(jobid,status,))
			self.conn.commit()
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error setting job status:' + str(e))
			return None

	def delete_job(self,job_id):
		try:
			self.cur.execute("DELETE FROM job WHERE id=%s  RETURNING id",(job_id,))
			res = self.cur.fetchall()
			self.conn.commit()
			if res[0]['id'] == job_id:
				return True
			else:
				return False
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error deleting job with:' + str(job_id) + str(e))
			return None

	def put_job(self,packageinstance,buildclient):
		try:
			self.cur.execute("INSERT INTO job (packageinstance_id,buildclient_id) VALUES (%s, %s)  RETURNING id",(packageinstance.id,(buildclient.id if buildclient else None)))
			res = self.cur.fetchall()
			self.conn.commit()

			return Job(res[0]['id'],packageinstance,buildclient)
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
				packages.append(Package(i['id'],i['version'],i['name']))
			return packages
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving packages list:' + str(e))
			return None

	def get_packages_byname(self, name):
		try:
			self.cur.execute("SELECT id,version,name FROM package WHERE name=%s",(name,))
			res = self.cur.fetchall()
			self.conn.commit()

			packages = []
			for i in res:
				packages.append(Package(i['id'],i['version'],i['name']))
			return packages
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving package with name:' + str(name) + str(e))
			return None

	def get_package_id(self,package_id):
		try:
			self.cur.execute("SELECT id,version,name FROM package WHERE id=%s",(package_id,))
			res = self.cur.fetchall()
			self.conn.commit()

			return Package(res[0]['id'],res[0]['version'],res[0]['name'])
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving package with id:' + str(package_id) + str(e))
			return None

	# TODO: return single instance instead of list?
	def get_package_byvalues(self,name,version):
		try:
			self.cur.execute("SELECT id,name,version FROM package WHERE name=%s AND version=%s",(name,version))
			res = self.cur.fetchall()
			self.conn.commit()

			packages = []
			for i in res:
				packages.append(Package(i['id'],i['version'],i['name']))
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

			return Package(res[0]['id'],version,name)
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error adding package:' + name + version + str(e))
			return None

	def delete_package(self,package_id):
		try:
			self.cur.execute("DELETE FROM package WHERE id=%s  RETURNING id",(package_id,))
			res = self.cur.fetchall()
			self.conn.commit()

			if res[0]['id'] == package_id:
				return True
			else:
				return False
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error deleting package with:' + str(package_id) + str(e))
			return None

	#<<<<<<<<< Packageinstance related Queries >>>>>>>

	def get_packageinstance_id(self,packageinstance_id):
		try:
			self.cur.execute("SELECT id,package_id,arch_id,suite_id,dist_id,format_id,master FROM packageinstance  WHERE id=%s",(packageinstance_id,))
			res = self.cur.fetchall()
			self.conn.commit()

			package = self.get_package_id(res[0]['package_id'])
			arch = self.get_arch_id(res[0]['arch_id'])
			suite = self.get_suite_id(res[0]['suite_id'])
			dist = self.get_dist_id(res[0]['dist_id'])
			pkg_format = self.get_format_id(res[0]['format_id'])
			return PackageInstance(res[0]['id'],package,arch,suite,dist,pkg_format,res[0]['master'])
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving package instance with:' + str(packageinstance_id) + str(e))
			return None

	def get_packageinstances(self):
		try:
			self.cur.execute("SELECT id,package_id,arch_id,suite_id,dist_id,format_id,master FROM packageinstance ORDER BY package_id, id")
			res = self.cur.fetchall()
			self.conn.commit()

			packageinstances = []
			for i in res:
				packageinstances.append(self.get_packageinstance_id(i['id']))
			return packageinstances
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving package instances list:' + str(e))
			return None

	def get_packageinstances_byname(self, name):
		try:
			self.cur.execute("SELECT packageinstance.id AS id,package.id AS package_id ,arch_id,suite_id,dist_id,format_id,master FROM packageinstance,package WHERE packageinstance.package_id = package.id AND name = %s ORDER BY package_id, id",(name,))
			res = self.cur.fetchall()
			self.conn.commit()

			packageinstances = []
			for i in res:
				packageinstances.append(self.get_packageinstance_id(i['id']))
			return packageinstances
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving package instances by name:' + str(e))
			return None

	# TODO: return single instance instead of list?
	def get_packageinstance_byvalues(self,package,arch,suite,dist,pkg_format):
		try:
			self.cur.execute("SELECT id,package_id,arch_id,suite_id,dist_id,format_id,master FROM packageinstance WHERE package_id=%s AND arch_id=%s AND suite_id=%s AND dist_id=%s AND format_id=%s",(package.id,arch.id,suite.id,dist.id,pkg_format.id))
			res = self.cur.fetchall()
			self.conn.commit()

			packageinstances = []
			for i in res:
				packageinstances.append(self.get_packageinstance_id(i['id']))
			return packageinstances
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving package instance by value:' + str(e))
			return None

	def put_packageinstance(self,package,arch,suite,dist,pkg_format,master):
		try:
			self.cur.execute("INSERT into packageinstance(package_id,arch_id,suite_id,dist_id,format_id,master) VALUES (%s, %s, %s, %s, %s, %s)  RETURNING id",(package.id,arch.id,suite.id,dist.id,pkg_format.id,master))
			self.conn.commit()
			res = self.cur.fetchall()
			self.conn.commit()

			return PackageInstance(res[0]['id'],package,arch,suite,dist,pkg_format,master)
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error adding package instance:' + package + arch + suite + dist + pkg_format + master + str(e))
			return None

	def delete_packageinstance(self,packageinstance_id):
		try:
			self.cur.execute("DELETE FROM packageinstance WHERE id=%s RETURNING id",(packageinstance_id,))
			res = self.cur.fetchall()
			self.conn.commit()

			if res[0]['id'] == packageinstance_id:
				return True
			else:
				return False
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error deleting package instance with:' + str(packageinstance_id) + str(e))
			return None

	# <<<<< TODO: This is a work in progress!!! >>>>>
	def check_specific_packageinstance_exists(self,arch,package,distribution,pkg_format,suite):
		try:
			if arch and distribution and pkg_format and package and suite:
				self.cur.execute("SELECT id FROM packageinstance WHERE arch_id=%s AND dist_id=%s AND format_id=%s AND package_id=%s AND suite_id=%s",(arch.id,distribution.id,pkg_format.id,package.id,suite.id))
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
				package_instances.append(PackageInstance(i['id'], i['package'], i['arch'], i['suite'], i['dist'], i['format'], i['master']))
			return package_instances
		except Exception as e:
			self.conn.rollback()
			raise Exception('Error retrieving package instance list:' + str(e))
			return None

	def get_supported_architectures(self,suite) :
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

myDb = Database() # singleton instance
