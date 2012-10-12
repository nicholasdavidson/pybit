#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       pybitclient-test.py
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

import unittest
import pybitclient
from pybitclient.debian import DebianBuildClient
from pybitclient.subversion import SubversionClient

class TestClient(unittest.TestCase) :
	def setUp (self):
		return

	def test_build_client (self) :
		deb_client = DebianBuildClient()
		svn_client = SubversionClient()

if __name__ == '__main__':
	unittest.main()
