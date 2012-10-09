#!/usr/bin/python

import psycopg2

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
		self.conn = psycopg2.connect(database="pybit", user="postgres", host="catbells", port="5432");
		self.cur = self.conn.cursor()

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
		return res

	def put_arch(self,id,name):
		self.cur.execute("INSERT into arch(id,name) VALUES (%s, %s)",(id,name))
		res = self.conn.commit()
		return res

	def get_dists(self):
		self.cur.execute("SELECT id,name FROM distribution ORDER BY name")
		res = self.cur.fetchall()
		return res

	def put_dist(self,id,name):
		self.cur.execute("INSERT into distribution(id,name) VALUES (%s, %s)",(id,name))
		res = self.conn.commit()
		return res

	def get_formats(self):
		self.cur.execute("SELECT id,name FROM format ORDER BY name")
		res = self.cur.fetchall()
		return res

	def put_format(self,id,name):
		self.cur.execute("INSERT into format(id,name) VALUES (%s, %s)",(id,name))
		res = self.conn.commit()
		return res

	def get_statuses(self):
		self.cur.execute("SELECT id,name FROM status ORDER BY name")
		res = self.cur.fetchall()
		return res

	def put_status(self,id,name):
		self.cur.execute("INSERT into status(id,name) VALUES (%s, %s)",(id,name))
		res = self.conn.commit()
		return res

	def get_suites(self):
		self.cur.execute("SELECT id,name FROM suite ORDER BY name")
		res = self.cur.fetchall()
		return res

	def put_suite(self,id,name):
		self.cur.execute("INSERT into suite(id,name) VALUES (%s, %s)",(id,name))
		res = self.conn.commit()
		return res

	#<<<<<<<< BuildD related database functions >>>>>>>>

	def get_buildclients(self):
		self.cur.execute("SELECT id,name FROM buildclients ORDER BY name")
		res = self.cur.fetchall()
		return res

	def get_buildd_id(self,id):
		self.cur.execute("SELECT id,name FROM buildclients WHERE id=%s",(id,))
		res = self.cur.fetchall()
		return res

	def put_buildclient(self,id,name):
		self.cur.execute("INSERT into buildclients(id,name) VALUES (%s, %s)",(id,name))
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
		return res

	def get_job(self,id):
		self.cur.execute("SELECT id,packageinstance_id,buildclient_id FROM job WHERE id=%s",(id,))
		res = self.cur.fetchall()
		return res

	def get_job_status(self,id):
		#TODO: work in progress
		self.cur.execute("SELECT job.id, status.name FROM job, jobstatus, status WHERE job.id=%s AND job.id = jobstatus.job_id AND job.status_id = status.id",(id,))
		res = self.cur.fetchall()
		return res

	def delete_job(self,id):
		self.cur.execute("DELETE FROM job WHERE id=%s",(id,))
		res = self.conn.commit()
		return res

	def put_job(self,id,packageinstance_id,buildclient_id):
		#TODO: work in progress
		self.cur.execute("INSERT INTO job (id,packageinstance_id,buildclient_id) VALUES (%s, %s, %s)",(id,packageinstance_id,buildclient_id))
		res = self.conn.commit()
		return res

	#<<<<<<<< Package related database functions >>>>>>>>
	# UPDATE queries?
	def get_packages(self):
		self.cur.execute("SELECT id,version,name FROM package ORDER BY name")
		res = self.cur.fetchall()
		return res

	def put_package(self,id,version,name):
		self.cur.execute("INSERT into package(id,version,name) VALUES (%s, %s, %s)",(id,name))
		res = self.conn.commit()
		return res

	def delete_package(self,id):
		self.cur.execute("DELETE FROM package WHERE id=%s",(id,))
		res = self.conn.commit()
		return res
