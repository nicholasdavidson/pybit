Debian Repository Watcher
#########################

Pybit-watcher provides a watcher daemon to monitor a nominated directory
for for Debian package uploads (``*.changes``), then runs the appropriate
incoming rule on the configured reprepro repository. This allows pybit
clients to upload without waiting for the packages to be processed by
the archive.

The watcher does depend on python. Also, the JSON configuration file
needs to be configured before it will process uploads.

To configure the watcher you need to perform several tasks, remove the
configured key at the top of the config file and set dry-run to false.

Each directory which the watcher will monitor becomes a section in the
config file. The absolute path to the directory where uploads will be
deposited is specified as a key in the rules section. (This changed in
0.5.0, the old rule value has been dropped.)

::

 {
    "rules": {
    "/absolute/path/repo/incoming" : {
        "repobase": "/absolute/path/repo",
        "rule" : "incoming_rule"
        }
    },
 }

  repobase
    The absolute path to the repository.

  rule
    The reprepro rule that will be run by the watcher when it detects
    a changes file.

The amount of time to wait after detecting a changes file and befor
running the rule, this is a cludge to fix races because certain upload
utilitys (dput) upload then mess with the uploaded files::

 {
   "sleeptime": 3
 }

To run the reprepro command as a particular user append a key containing
the user to the config file::

 { 
   "user": "buildd"
 }
