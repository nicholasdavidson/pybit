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
import jsonpickle

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

	def __init__(self,msg_body=''):
		if msg_body:
			self = jsonpickle.decode (msg_body)

def send_message (chan, pkg, key):
	msg.amqp.Message(jsonpickle.encode(pkg))
	msg.properties["delivery_mode"] = 2
	chan.basic_publish(msg,exchange=pkg.architecture,routing_key=key)

def run_cmd (cmd, fail_msg, report, simulate):
	if simulate :
		print cmd
		return True
	else:
		if os.system (command) :
			pkg.msgtype = fail_msg
			msg.amqp.Message(jsonpickle.encode(pkg))
			msg.properties["delivery_mode"] = 2
			chan.basic_publish(msg,exchange=pkg.architecture,routing_key=report)
			return False
	return True
