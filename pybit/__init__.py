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
import optparse

def merge_options(settings, options_group, options):
	if not isinstance(options_group, optparse.OptionGroup):
		print "E: options must be an instance of optparse.OptionsGroup."
		return {}
	if settings is None:
		print "E: can't merge a null settings dictionary."
		return {}
	verbose = False
	if hasattr(options,'verbose'):
		verbose = options.verbose

	for option in options_group.option_list :
		value = getattr(options, option.dest)
		if value is not None and value is not "":
			settings[option.dest] = value
			if verbose == True:
				print "Setting %s to %s" % (option.dest, value)
		else:
			if verbose == True:
				if option.dest in settings :
					print "Leaving %s as %s" % (option.dest, settings[option.dest])
				else:
					print "No such value %s" % option.dest


	return settings



def get_client_queue(client_id):
	return "build_client_%s" % client_id

def get_build_queue_name(dist, arch, suite, package):
	return "%s_%s_%s_%s" % (dist, arch, suite, package)

def get_build_route_name(dist, arch, suite, package):
	return "%s.%s.%s.%s" % (dist, arch, suite, package)

def load_settings(path):
	opened_file = None
	opened_path = path
	settings = {}
	#try the unmodified path incase we're being passed an absolute path.
	try:
		opened_file = open(path)
	except IOError:
		opened_path = "./configs/%s" % path
		try:
			opened_file = open(opened_path, 'r')
		except IOError:
			opened_path = "/etc/pybit/%s" % path
			try:
				opened_file = open(opened_path)
			except IOError:
				pass
	if opened_file:
		encoded_string = opened_file.read()
		try:
			settings = jsonpickle.decode(encoded_string ) 
		except ValueError :
			print "Couldn't load any settings files."
	
	return (settings, opened_path)

exchange_name="pybit"
status_route="pybit.control.status"
status_queue="pybit_status"
