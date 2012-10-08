#!/usr/bin/python

import psycopg2

class db:

	conn = None
	cur = None

	def __init__(self):
		self.connect()

	def connect(self):
		self.conn = psycopg2.connect(database="pybit", user="postgres", host="catbells", port="5432");
		self.cur = self.conn.cursor()

	def disconnect(self):
		self.conn.commit()
		self.cur.close()
		self.conn.close()

	def get_arches(self):
		self.cur.execute("SELECT id,name FROM arch")
		res = self.cur.fetchall()
		return res

	def get_buildclients(self):
		self.cur.execute("SELECT id,name FROM buildclients")
		res = self.cur.fetchall()
		return res

	def get_buildd_id(self,id):
		self.cur.execute("SELECT id,name FROM buildclients WHERE id=%s",(id,))
		res = self.cur.fetchall()#]
		return res

	def get_buildd_jobs(self,id):
		self.cur.execute("SELECT job.id,buildclients.id FROM buildclients,job WHERE buildclients.id=%s AND buildclients.id = job.buildclient_id",(id,))
		res = self.cur.fetchall()#]
		return res

	def get_distributions(self):
		self.cur.execute("SELECT id,name FROM distribution")
		res = self.cur.fetchall()
		return res

	def get_formats(self):
		self.cur.execute("SELECT id,name FROM format")
		res = self.cur.fetchall()
		return res

	def get_jobs(self):
		self.cur.execute("SELECT id,packageinstance_id,buildclient_id,status_id FROM job")
		res = self.cur.fetchall()
		return res

	def get_job(self,id):
		self.cur.execute("SELECT id,packageinstance_id,buildclient_id,status_id FROM job WHERE id=%s",(id,))
		res = self.cur.fetchall()
		return res

	def delete_job(self,id):
		self.cur.execute("DELETE FROM job WHERE id=%s",(id,))
		res = self.conn.commit()
		return res

	def put_job(self,id,packageinstance_id,buildclient_id,status_id):
		#TODO: work in progress
		self.cur.execute("INSERT INTO job (id,packageinstance_id,buildclient_id,status_id) VALUES (%s, %s, %s, %s)",(id,packageinstance_id,buildclient_id,status_id))
		res = self.conn.commit()
		return res

	def get_packages(self):
		self.cur.execute("SELECT id,version,name FROM package")
		res = self.cur.fetchall()
		return res

	def get_statuses(self):
		self.cur.execute("SELECT id,name FROM status")
		res = self.cur.fetchall()
		return res

	def get_suites(self):
		self.cur.execute("SELECT id,name FROM suite")
		res = self.cur.fetchall()
		return res

	def get_job_status(self,id):
		self.cur.execute("SELECT job.id, status.name FROM job, status WHERE job.id=%s AND job.status_id = status.id",(id,))
		res = self.cur.fetchall()
		return res
