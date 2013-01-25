#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       setup.py
#
#       Copyright 2012 Neil Williams <codehelp@debian.org>
#       Copyright (C) 2006 James Westby <jw+debian@jameswestby.net>
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

from setuptools import setup

setup(name='pybit',
	version='0.4.2',
	description='PyBit buildd integrated toolkit',
	license='gpl2',
	url='https://github.com/nicholasdavidson/pybit.git',
	packages=['pybit', 'pybitclient', 'pybitweb',],
	maintainer='TCL Build System user',
	maintainer_email='rnd@toby-churchill.com',
	include_package_data = True,
	exclude_package_data = { 'pybitclient' : [ 'sbuild-cross.sh' , 'sbuild-orig.sh', 'README'],
	'pybitweb' : [ 'static/*' ]
	}
	)

