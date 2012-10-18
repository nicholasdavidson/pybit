#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       buildclient.py
#
#       Copyright 2012 Neil Williams <codehelp@debian.org>
#
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

from amqplib import client_0_8 as amqp
import os
import jsonpickle
import subprocess
import shlex
import pybitclient

class BuildClient(object):

	def __init__(self):
		self.build_process = None
		return

	def send_message (self, chan, pkg, key):
		try:
			msg = amqp.Message(jsonpickle.encode(pkg))
			msg.properties["delivery_mode"] = 2
			chan.basic_publish(msg,exchange=pkg.architecture,routing_key=key)
		except Exception as e:
			raise Exception('Error sending message from client: ' + str(e))
			return

	def run_cmd (self, cmd, fail_msg, pkg, report, simulate):
		try:
			if simulate == True :
				print cmd
				return True
#			elif not self.build_process :
#				self.build_process = subprocess.Popen(shlex.split(command))
			else:
				if os.system (cmd) :
					pkg.msgtype = fail_msg
					msg = amqp.Message(jsonpickle.encode(pkg))
					msg.properties["delivery_mode"] = 2
#					chan.basic_publish(msg,exchange=pkg.architecture,routing_key=report)
					print "E: Failed to run %s" % (cmd)
					return False
			return True
		except Exception as e:
			raise Exception('Error running command: ' + str(e))
			return

	def is_dry_run (self):
		if (not hasattr(self, 'options')) :
			return False
		if (not "dry_run" in self.options) :
			return False
		return self.options["dry_run"]

	def fetch_source (self):
		pass

	def build_master (buildroot):
		pass

	def build_slave (buildroot):
		pass

	def update_environment (self,name,pkg) :
		pass

	def upload (self) :
		pass

	def is_building (self) :
		if not self.build_process :
			return False
		if self.build_process.poll() == None :
			return False
		return True

	def cancel (self) :
		try:
			if not self.build_process :
				return
			if self.build_process.poll() == None : # None if still running
				self.build_process.terminate()
		except Exception as e:
			raise Exception('Error cancelling: ' + str(e))
			return
