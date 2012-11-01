import jsonpickle
import os
import sys
from os.path import isfile
        
def load_from_cwd(filename):
    try:
        #print "DEBUG: Opening local file" , filename
        path = "%s/configs/%s" % (os.getcwd(),filename);
        
        if isfile(path): # exists
            settings_file = open(path, 'r')
            if settings_file: # can actually open it
                encoded_string = settings_file.read()
                settings = jsonpickle.decode(encoded_string )
                #print "DEBUG: Opened local config file", path
                return settings
            else:
                #print "ERROR: Error loading local file: ", path
                return None
        else:
            #print "ERROR: Error loading local file from path: ", path
            return None
    except Exception as e:
            raise Exception('Error loading local file:' + filename + str(e))
            return None

def load_from_etc(filename):
    try:
        #print "DEBUG: Opening config file" , filename
        path = "/etc/pybit/configs/%s" % (filename);
        
        if isfile(path): # exists
            settings_file = open(path, 'r')
            if settings_file: # can actually open it
                encoded_string = settings_file.read()
                settings = jsonpickle.decode(encoded_string )
                #print "DEBUG: Opened config file", path
                return settings
            else:
                #print "ERROR: Error loading config file: ", path
                return None
        else:
            #print "ERROR: Error loading config file from path: ", path
            return None
    except Exception as e:
            raise Exception('Error loading config file:' + filename + str(e))
            return None

def load_settings_from_file(filename):
    try:
        print "DEBUG: Loading settings file:" , filename, "....."
        localsettings = load_from_cwd(filename)
        globalsettings = load_from_etc(filename)
        
        #print "Local settings: " + repr(localsettings) + "Global settings: " + repr(globalsettings)
        
        if localsettings:
            print "DEBUG: Using local settings file"
            return localsettings
        elif globalsettings:
            print "DEBUG: Using system settings file"
            return globalsettings
        else:
            raise Exception # not loading settings is fatal, bail out
            return None
    except Exception as e:
            print ("FATAL ERROR: Error loading settings from: " + filename)
            sys.exit(-1)
            return False