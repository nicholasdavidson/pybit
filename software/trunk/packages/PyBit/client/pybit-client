#!/usr/bin/python

# -*- coding: utf-8 -*-
#
#       client.py
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

# Needs rabbitmq-server python-amqplib python-debian
from amqplib import client_0_8 as amqp
import re
import json
import os.path
import time
#from helpers import get_settings, deb_package, send_message
#from helpers import get_settings, deb_package
from debian.changelog import Changelog, Version

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
	except:
		raise Exception,"Unhandled JSON error"
		return

# Specific buildd options

# FIXME: decide how this is managed and packaged
options =  get_settings("client.conf")

host_arch = options["host_arch"] # i386
use_lvm = options["use_lvm"] # true
role = options["role"] # master - builds Architecture: all packages.
buildroot = options["buildroot"]
host_opt = options["host"]
port_opt = options["port"]
userid_opt = options["userid"]
pass_opt = options["password"]
vhost_opt = options["virtual_host"]
insist_opt = True if options["insist"] == "True" else False
addr_opt = host_opt + ":" + port_opt
dput_opt = options["dput"]
buildd_id = options["idstring"]

########## No configuration beyond this stage ##############

# PyBit setup variables - package content
queue_name = "rabbit"
report_name = "controller"
listening_name = "buildd"
dput_cfg = "/etc/pybit/dput.cf"

# variables to retrieve from the job object later
dput_dest = "tcl"

conn = amqp.Connection(host=addr_opt, userid=userid_opt, password=pass_opt, virtual_host=vhost_opt, insist=insist_opt)
chan = conn.channel()
chan.queue_declare(queue=queue_name, durable=True, exclusive=False, auto_delete=False)
chan.exchange_declare(exchange=host_arch, type="direct", durable=True, auto_delete=False,)
chan.queue_bind(queue=queue_name, exchange=host_arch, routing_key=listening_name)

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

def recv_callback(msg):
	pkg = deb_package (msg.body)
	if not pkg:
		print "could not parse message"
		return
	if not dput_dest or dput_dest == "":
		print "refusing to upload to default dput destination (Debian ftpmaster)"
		pkg.msgtype = "failed"
		send_message (chan, pkg, report_name)
		return
	if not buildd_id or buildd_id == "default":
		print "refusing to build without a default or empty idstring"
		pkg.msgtype = "failed"
		send_message (chan, pkg, report_name)
		return
	srcdir= buildroot + "/" + pkg.suite + "/svn"
	builddir= buildroot + "/tmpbuilds/" + pkg.suite
	# FIXME: allow to support cross once the routing_key check is proven.
	if pkg.buildd == host_arch + "-" + "buildd":
		return
	# FIXME: use same naming convention in schroot setup whether lvm is used or not.
	if use_lvm :
		name = pkg.suite + "-source"
	else:
		name = pkg.suite
	command = "schroot -u root -c " + name + "-- apt-get update > /dev/null 2>&1"
	if run_cmd (command, "failed", report_name, options["dry_run"]):
		return
	# May need more sanity checking here
	pkg.architecture = host_arch
	pkg.buildd = buildd_id
	pkg.msgtype = "building"
	send_message (chan, pkg, report_name)
	if role == "master" :
		package_dir = srcdir + "/" + pkg.package
		if os.path.isdir(package_dir) :
			os.chdir (package_dir)
			command = "dpkg-checkbuilddeps"
			if run_cmd (command, "build-dep-wait", report_name, options["dry_run"]):
				return
		command = "dpkg-buildpackage -S -d > /dev/null 2>&1"
		if run_cmd (command, "failed", report_name, options["dry_run"]):
			return
		command = "sbuild -A -s -d " + pkg.suite + srcdir + "/" + pkg.source + "_" + pkg.version + ".dsc";
		if run_cmd (command, "failed", report_name, options["dry_run"]):
			return
		changes = builddir + "/" + pkg.package + "_" + pkg.version + "_" + pkg.architecture + ".changes"
		if not os.path.isfile (changes) :
			pkg.msgtype = "failed"
			send_message (chan, pkg, report_name)
			return
	else :
		if role == "slave":
			command = "sbuild -d " + pkg.suite + " " + pkg.source + "_" + pkg.version;
			if run_cmd (command, "failed", report_name, options["dry_run"]):
				return
			changes = builddir + "/" + pkg.package + "_" + pkg.version + "_" + pkg.architecture + ".changes"
			if not os.path.isfile (changes) :
				pkg.msgtype = "failed"
				send_message (chan, pkg, report_name)
				return
	command = "dput -c " + dput_cfg + " " + dput_opt + " " dput_dest + " " changes
	if run_cmd (command, "failed", report_name, options["dry_run"]):
		return
	pkg.msgtype = "uploaded"
	send_message (chan, pkg, report_name)

while True:
	chan.wait()

chan.close()
conn.close()
