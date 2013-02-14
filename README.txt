pyBit (πβ or πβιϑ) itself is what it says on the tin, the Python Build Integration Toolkit.

The aim was to create a distributed AMQP based build system system using python and RabbitMQ. We talk to the queue using python-amqplib, with messages being encoded using python-jsonpickle. python-bottle is used to provide a lightweight HTTP based API, which the associated (static) web GUI can query using the jQuery javascript library.

Design
The system consists of two parts, a single server, and one to many clients. pybit-web is the server part, and pybit-client the client part. You will also need a PostgreSQL database, which we speak to using python-psycopg2.

The front-end (Static HTML) web GUI queries the back-end (python) HTTP API using the jQuery Javascript library. The [HTML side] of the web GUI is not coupled otherwise to the system, as it does not speak to the queue or database directly.

Likewise, the client only speaks to the controller using the queue, and the HTTP API, never the database. By loosely coupling components, we aim to make it easy to extend the system to support a variety of different configurations and scenarios.

We aim to be flexible enough to build any combination of package type (i.e. DEB, RPM) for any arch, for any system (even, say .MSI installers for MS Windows). Currently however, we are mostly concerned with building ARM and i386 packages targeting Debian GNU/Linux 'Squeeze', and above, as this is what we develop on/for internally.

Data Exchange
We use a well known interchange format (JSON, with the JSONPickle library). We will present a RESTful HTTP based API. i.e. using the GET verb on http://[server]/job shall return a list of all running build jobs, while http://[server]/job/1 shall return the specific job instance with the ID 1.

Note that we proxy POST and PUT, and map /[object]/[id]/delete to DELETE. This is as HTML forms, in most browsers can only do GET and POST (JQuery can do more using its AJAX functions).

Requirements
Note that bottle.py, although in the debian repos as python-bottle, does not depend on any external libraries. Therefore, we include our own bottle.py from upstream. We need this as the new route rule syntax, amongst other things, was introduced in Bottle 0.10. Debian squeeze has 0.8x.

python-requests is available from squeeze-backports, as is python-psycopg2. Do NOT use the version of psycopg2 from squeeze/main, if you intend to use a multi-threaded web server, this is unsupported.

Installation
In /db, there are scripts to create and populate the database manually. However, we reccomend you use the dbconfig-common wizard, during the package installation process.

Running the software
The connection string, hostname, etc.... are stored in /etc/pybit/configs/*. These should be set during the package installation process, but you may edit and configure these as you wish. Then simply start the server first, then the client(s) second. The client will pick up any suitable queued jobs when it comes up.

For support:
IRC - #pybit on irc.oftc.net irc://irc.oftc.net/pybit (Or use github issues)

Packaging requirements

* rabbitmq-server http://packages.qa.debian.org/r/rabbitmq-server.html
      o http://www.rabbitmq.com/
* python-amqplib http://packages.qa.debian.org/p/python-amqplib.html
      o http://code.google.com/p/py-amqplib/
* python-debian http://packages.qa.debian.org/p/python-debian.html
* python-jsonpickle http://packages.qa.debian.org/j/jsonpickle.html
* python-bottle http://packages.qa.debian.org/p/python-bottle.html
      o http://bottlepy.org/
* python-psycopg2 http://packages.qa.debian.org/p/psycopg2.html
* python-requests http://packages.qa.debian.org/p/python-requests.html
Useful links:

* http://www.rabbitmq.com/tutorials/tutorial-one-python.html - A RabbitMQ tutorial using Python.
* http://jsonpickle.github.com/
* http://initd.org/psycopg/
* http://www.rabbitmq.com/
* http://bottlepy.org/docs/stable/index.html
* http://docs.python-requests.org/en/latest/
