#!/usr/bin/python

# Change working directory so relative paths (and template lookup) work again
import os
os.chdir(os.path.dirname(__file__))

import jsonpickle
import optparse
import site

site.addsitedir('/home/jamesb/pybit')
site.addsitedir('/home/jamesb/pybit/pybit')
site.addsitedir('/home/jamesb/pybit/pybitweb')

import pybit
import pybitweb
from pybitweb.db import Database
from pybitweb.controller import Controller

settings = pybit.load_settings("web.conf")
myDb = Database(settings['db']) # singleton instance
buildController = Controller(settings['controller'], myDb) # singleton instance
application = pybitweb.get_app(settings,myDb,buildController)
