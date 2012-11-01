import jsonpickle
import os

#       Copyright 2012:
#
#       Nick Davidson <nickd@toby-churchill.com>,
#       Simon Haswell <simonh@toby-churchill.com>,
#       Neil Williams <neilw@toby-churchill.com>,
#       James Bennet <github@james-bennet.com / James.Bennet@toby-churchill.com>

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

def get_client_queue(id):
	return "build_client_%s" % id

def get_build_queue_name(dist, arch, suite, package):
	return "%s_%s_%s_%s" % (dist, arch, suite, package)

def get_build_route_name(dist, arch, suite, package):
	return "%s.%s.%s.%s" % (dist, arch, suite, package)

def load_settings(file):
	settings_file = None
	path = "./configs/%s" % file
	try:
		settings_file = open(path, 'r')
	except IOError as e:
		path = "/etc/pybit/%s" % file
		try:
			settings_file = open(path)
		except IOError as e:
			pass
	if settings_file:
		encoded_string = settings_file.read()
		return jsonpickle.decode(encoded_string )
	else:
		return {}

exchange_name="pybit"
status_route="pybit.control.status"
status_queue="pybit_status"
