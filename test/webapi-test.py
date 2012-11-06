#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       untitled.py
#
#       Copyright 2012 simonh <simonh@simonhpc>
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

#from common.models import transport, packageinstance, job
import logging
import sys
import unittest

class TestWeb(unittest.TestCase) :
	def setUp (self):
		return

	def test_01 (self) :
		return

if __name__ == '__main__':
	FORMAT = '%(msg)s'
	logging.basicConfig(format=FORMAT)
	logging.basicConfig( stream=sys.stderr )
	logging.getLogger( "testCase" ).setLevel( logging.DEBUG )
	suite = unittest.TestLoader().loadTestsFromTestCase(TestWeb)
	unittest.TextTestRunner(verbosity=2).run(suite)
	runner = unittest.TextTestRunner(verbosity=2)
	res = runner.run(suite)
	if not res.wasSuccessful() :
		sys.exit (1)
