#       daemonlogger.py
#
#       Copyright 2010 Bud P. Bruegger <bud@sistema.it>
#       Created on Mon, 25 Oct 2010
#       http://code.activestate.com/recipes/577442-logging-support-for-python-daemon/
#
#       BSD Licence
#
#       Redistribution and use in source and binary forms, with or without
#       modification, are permitted provided that the following conditions are
#       met:
#
#       * Redistributions of source code must retain the above copyright
#         notice, this list of conditions and the following disclaimer.
#       * Redistributions in binary form must reproduce the above
#         copyright notice, this list of conditions and the following disclaimer
#         in the documentation and/or other materials provided with the
#         distribution.
#       * Neither the name of the author nor the names of its
#         contributors may be used to endorse or promote products derived from
#         this software without specific prior written permission.
#
#       THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#       "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#       LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#       A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#       OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#       SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#       LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#       DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#       THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#       (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#       OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import sys
from logging import Logger
import daemon

class FileLikeLogger:
	"wraps a logging.Logger into a file like object"

	def __init__(self, logger):
		self.logger = logger

	def write(self, str):
		str = str.rstrip() #get rid of all tailing newlines and white space
		if str: #don't log emtpy lines
			for line in str.split('\n'):
				self.logger.critical(line) #critical to log at any logLevel

	def flush(self):
		for handler in self.logger.handlers:
			handler.flush()

	def close(self):
		for handler in self.logger.handlers:
			handler.close()

def openFilesFromLoggers(loggers):
	"returns the open files used by file-based handlers of the specified loggers"
	openFiles = []
	for logger in loggers:
		for handler in logger.handlers:
			if hasattr(handler, 'stream') and \
			   hasattr(handler.stream, 'fileno'):
				openFiles.append(handler.stream)
	return openFiles

class LoggingDaemonContext(daemon.DaemonContext):

	def _addLoggerFiles(self):
		"adds all files related to loggers_preserve to files_preserve"
		for logger in [self.stdout_logger, self.stderr_logger]:
			if logger:
				self.loggers_preserve.append(logger)
		loggerFiles = openFilesFromLoggers(self.loggers_preserve)
		self.files_preserve.extend(loggerFiles)

	def __init__(
		self,
		chroot_directory=None,
		working_directory='/',
		umask=0,
		uid=None,
		gid=None,
		prevent_core=True,
		detach_process=None,
		files_preserve=[],   # changed default
		loggers_preserve=[], # new
		pidfile=None,
		stdout_logger = None,  # new
		stderr_logger = None,  # new
		#stdin,   omitted!
		#stdout,  omitted!
		#sterr,   omitted!
		signal_map=None,
		):

		self.stdout_logger = stdout_logger
		self.stderr_logger = stderr_logger
		self.loggers_preserve = loggers_preserve

		devnull_in = open(os.devnull, 'r+')
		devnull_out = open(os.devnull, 'w+')
		files_preserve.extend([devnull_in, devnull_out])

		daemon.DaemonContext.__init__(self,
			chroot_directory = chroot_directory,
			working_directory = working_directory,
			umask = umask,
			uid = uid,
			gid = gid,
			prevent_core = prevent_core,
			detach_process = detach_process,
			files_preserve = files_preserve,
			pidfile = pidfile,
			stdin = devnull_in,
			stdout = devnull_out,
			stderr = devnull_out,
			signal_map = signal_map)

	def open(self):
		self._addLoggerFiles()
		daemon.DaemonContext.open(self)
		if self.stdout_logger:
			fileLikeObj = FileLikeLogger(self.stdout_logger)
			sys.stdout = fileLikeObj
		if self.stderr_logger:
			fileLikeObj = FileLikeLogger(self.stderr_logger)
			sys.stderr = fileLikeObj

