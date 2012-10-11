#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       client-common.py
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

import re
import os
import json

def get_settings(path):
	# dumps() serializes a python object to a JSON formatted string.
	# loads() deserializes a JSON formatted string to a python object.
	try:
		fh = open(path,"r")
		file_contents = fh.read();
		return json.loads(file_contents)
	except IOError:
		raise IOError,"Cannot load settings file."
		return
	except Exception:
		raise Exception,"Unhandled JSON error"
		return

class deb_package:

	#fields
	package = ""
	version = ""
	architecture = ""
	suite = ""
	buildd = ""
	msgtype = ""
	source = ""

	def __init__(self,msg_body=''):
		if msg_body:
			match = re.match ("(.*):(.*):(.*):(.*):(.*):(.*)", msg_body)

			if not match:
				raise Exception,"Regex error. Invalid format?"
				return
			else:
				self.package = match.group(1)
				self.version = match.group(2)
				self.architecture = match.group(3)
				self.suite = match.group(4)
				self.buildd = match.group(5)
				self.msgtype = match.group(6)

	def __str__(self):
		return self.package + ":" + self.version + ":" + self.architecture + ":" + self.suite + ":" + self.buildd + ":" + self.msgtype

	def __repr__(self):
		return self.package + ":" + self.version + ":" + self.architecture + ":" + self.suite + ":" + self.buildd + ":" + self.msgtype

	def __unicode__(self):
		return self.package + ":" + self.version + ":" + self.architecture + ":" + self.suite + ":" + self.buildd + ":" + self.msgtype

def send_message (chan, pkg, key):
	msg.amqp.Message(str(pkg))
	msg.properties["delivery_mode"] = 2
	chan.basic_publish(msg,exchange=pkg.architecture,routing_key=key)

def run_cmd (cmd, fail_msg, report, simulate):
	if simulate :
		print cmd
		return True
	else:
		if os.system (command) :
			pkg.msgtype = fail_msg
			msg.amqp.Message(str(pkg))
			msg.properties["delivery_mode"] = 2
			chan.basic_publish(msg,exchange=pkg.architecture,routing_key=report)
			return False
	return True
