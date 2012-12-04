#!/usr/bin/python

# Change working directory so relative paths (and template lookup) work again
import os
os.chdir(os.path.dirname(__file__))

import jsonpickle
import optparse
import site
import pybit
import pybitweb
from pybitweb.db import Database
from pybitweb.controller import Controller

(settings, opened_path) = pybit.load_settings("web/web.conf")
myDb = Database(settings['db']) # singleton instance
buildController = Controller(settings, myDb) # singleton instance
application = pybitweb.get_app(settings,myDb,buildController)
