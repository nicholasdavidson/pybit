#!/usr/bin/python

import psycopg2
import psycopg2.extras
from models import arch,dist,format,status,suite,buildd,job,package,packageinstance

#TODO: make more robust.

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
		self.conn = psycopg2.connect(database="pybit", user="postgres", host="catbells", port="5432")
		self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

	#When to call this? - Does python have deconstructors?
	def disconnect(self):
		self.conn.commit()
		self.cur.close()
		self.conn.close()

	#<<<<<<<< Lookup table queries >>>>>>>>
	# Do we care about update or delete?

	def get_arches(self):
		self.cur.execute("SELECT id,name FROM arch ORDER BY name")
		res = self.cur.fetchall()
		
		arches = []
		for i in res:
			arches.append(arch(i['id'],i['name']))
		return arches

	def put_arch(self,name):
		self.cur.execute("INSERT into arch(name) VALUES (%s)",(name,))
		res = self.conn.commit()
		return res

	def get_dists(self):
		self.cur.execute("SELECT id,name FROM distribution ORDER BY name")
		res = self.cur.fetchall()
		
		dists = []
		for i in res:
			dists.append(dist(i['id'],i['name']))
		return dists

	def put_dist(self,name):
		self.cur.execute("INSERT into distribution(name) VALUES (%s)",(name,))
		res = self.conn.commit()
		return res

	def get_formats(self):
		self.cur.execute("SELECT id,name FROM format ORDER BY name")
		res = self.cur.fetchall()
		
		formats = []
		for i in res:
			formats.append(format(i['id'],i['name']))
		return formats

	def put_format(self,name):
		self.cur.execute("INSERT into format(name) VALUES (%s)",(name,))
		res = self.conn.commit()
		return res

	def get_statuses(self):
		self.cur.execute("SELECT id,name FROM status ORDER BY name")
		res = self.cur.fetchall()
		
		statuses = []
		for i in res:
			statuses.append(status(i['id'],i['name']))
		return statuses

	def put_status(self,name):
		self.cur.execute("INSERT into status(name) VALUES (%s)",(name,))
		res = self.conn.commit()
		return res

	def get_suites(self):
		self.cur.execute("SELECT id,name FROM suite ORDER BY name")
		res = self.cur.fetchall()
		
		suites = []
		for i in res:
			suites.append(suite(i['id'],i['name']))
		return suites

	def put_suite(self,name):
		self.cur.execute("INSERT into suite(name) VALUES (%s)",(name,))
		res = self.conn.commit()
		return res

	#<<<<<<<< BuildD related database functions >>>>>>>>

	def get_buildclients(self):
		self.cur.execute("SELECT id,name FROM buildclients ORDER BY name")
		res = self.cur.fetchall()

		buildds = []
		for i in res:
			buildds.append(buildd(i['id'],i['name']))
		return buildds

	def get_buildd_id(self,id):
		self.cur.execute("SELECT id,name FROM buildclients WHERE id=%s",(id,))
		res = self.cur.fetchall()

		buildds = []
		for i in res:
			buildds.append(buildd(i['id'],i['name']))
		return buildds

	def put_buildclient(self,name):
		self.cur.execute("INSERT into buildclients(name) VALUES (%s)",(name,))
		res = self.conn.commit()
		return res

	def delete_buildclient(self,id):
		self.cur.execute("DELETE FROM buildclients WHERE id=%s",(id,))
		res = self.conn.commit()
		return res

	def get_buildd_jobs(self,id):
		self.cur.execute("SELECT job.id,buildclients.id FROM buildclients,job WHERE buildclients.id=%s AND buildclients.id = job.buildclient_id  ORDER BY job.id",(id,))
		res = self.cur.fetchall()
		return res

	#<<<<<<<< Job related database functions >>>>>>>>
	# UPDATE queries?

	def get_jobs(self):
		self.cur.execute("SELECT id,packageinstance_id,buildclient_id FROM job ORDER BY id")
		res = self.cur.fetchall()

		jobs = []
		for i in res:
			jobs.append(job(i['id'],i['packageinstance'],i['buildclient_id']))
		return jobs

	def get_job(self,id):
		self.cur.execute("SELECT id,packageinstance_id,buildclient_id FROM job WHERE id=%s",(id,))
		res = self.cur.fetchall()

		jobs = []
		for i in res:
			jobs.append(job(i['id'],i['packageinstance'],i['buildclient_id']))
		return jobs

	def get_job_status(self,id):
		#TODO: work in progress
		self.cur.execute("SELECT job.id, status.name FROM job, jobstatus, status WHERE job.id=%s AND job.id = jobstatus.job_id AND job.status_id = status.id",(id,))
		res = self.cur.fetchall()
		return res

	def delete_job(self,id):
		self.cur.execute("DELETE FROM job WHERE id=%s",(id,))
		res = self.conn.commit()
		return res

	def put_job(self,packageinstance_id,buildclient_id):
		#TODO: work in progress
		self.cur.execute("INSERT INTO job (packageinstance_id,buildclient_id) VALUES (%s, %s)",(packageinstance_id,buildclient_id))
		res = self.conn.commit()
		return res

	#<<<<<<<< Package related database functions >>>>>>>>
	# UPDATE queries?
	def get_packages(self):
		self.cur.execute("SELECT id,version,name FROM package ORDER BY name")
		res = self.cur.fetchall()

		packages = []
		for i in res:
			packages.append(package(i['id'],i['version'],i['name']))
		return packages

	def put_package(self,version,name):
		self.cur.execute("INSERT into package(version,name) VALUES (%s, %s)",(version,name))
		res = self.conn.commit()

		packages = []
		for i in res:
			packages.append(package(i['id'],i['version'],i['name']))
		return packages

	def delete_package(self,id):
		self.cur.execute("DELETE FROM package WHERE id=%s",(id,))
		res = self.conn.commit()

		packages = []
		for i in res:
			packages.append(package(i['id'],i['version'],i['name']))
		return packages
	#<<<<<<<<< Report Queries >>>>>>>
	def get_report_package_instance(self):
		self.cur.execute("SELECT packageinstance.id, suite.name AS suite, package.name AS package, package.version AS version, arch.name AS arch, format.name AS format, distribution.name AS dist FROM packageinstance LEFT JOIN arch ON arch.id=arch_id LEFT JOIN suite ON suite.id=suite_id LEFT JOIN distribution ON distribution.id=dist_id LEFT JOIN package ON package_id=package.id LEFT JOIN format ON format_id=format.id")
		res = self.cur.fetchall()
		
		package_instances = []
		for i in res :
			print i
			package_instances.append(packageinstance(i['id'], i['suite'], i['package'], i['version'], i['arch'], i['format'], i['dist']))
		return package_instances
