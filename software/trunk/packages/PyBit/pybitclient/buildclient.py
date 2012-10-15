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
import pybitclient

class BuildClient(object):

	def __init__(self):
		return

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

	def fetch_source (self):
		pass

	def build_master (buildroot):
		pass

	def build_slave (buildroot):
		pass

	def update_environment (self) :
		pass

	def upload (self) :
		pass
