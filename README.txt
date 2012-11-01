pyBit (πβ or πβιϑ) - python Buildd Integration Toolkit - a buildd system using python and RabbitMQ. Note that this system is modelled in Enterprise Architect, this file may not always be up-to-date.

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

Packaging Notes
We will debian package using python-setuptools (http://packages.qa.debian.org/p/pyth...etuptools.html). Bottle, althogh in the debian repos as python-bottle, does not depend on any external libraries. Therefore, we include our own bottle.py from upstream. We need this as the new route rule syntax, amongst other things, was introduced in Bottle 0.10. Debian squeeze has 0.8x. python-requests is available from squeeze-backports.

We use a well known interchange format (JSON, with the JSONPickle library). For example, a job will serialise to something like:

{"py/object": "pybit.models.Job","id": 2,"packageinstance": {"py/object": "pybit.models.PackageInstance","package": {"py/object": "pybit.models.Package","version": "0.4.42","id": 1,"name": "logicalmodel"},"format": {"py/object": "pybit.models.Format","id": 1,"name": "deb"},"master": false,"suite": {"py/object": "pybit.models.Suite","id": 2,"name": "development"},"distribution": {"py/object": "pybit.models.Dist","id": 1,"name": "Debian"},"arch": {"py/object": "pybit.models.Arch","id": 1,"name": "armel"},"id": 3},"buildclient": {"py/object": "pybit.models.BuildD","id": 1,"name": "arm01"}}

We will present a RESTful HTTP based API. i.e. GET http://buildcontroller/jobs?arch=i386 should return a list of all running build jobs for i386.
This is useful so we can in future plug other things into the system, without them having to know how it works internally. Note that we proxy POST to PUT, this is as HTML forms in most browsers can only do GET and POST (JQuery can do more).

Sample Data:
To populate or reset the database use:
$ psql --user postgres --host catbells pybit
 
Then do:
pybit=# \i <path to checkout>/software/trunk/packages/PyBit/db/schema.sql
pybit=# \i <path to checkout>/software/trunk/packages/PyBit/db/populate.sql
 
The connection string is in db.py under /webapi.

Run pybit.web.py and pybit-client.py to run it. You can test using curl like:

    * curl -i -X GET http://0.0.0.0:8080/arch
    * curl -i -X PUT http://localhost:8080/arch --data "name=test"
    * curl -X POST http://localhost:8080/job/vcshook --data "uri=http://svn.tcl.office/svn/lwdev&directory=software/branches/software_release_chickpea/packages/appbarwidget&method=svn&distribution=Debian&vcs_id=20961&architecture_list=all,any&package_version=0.6.33chickpea94&package=appbarwidget&suite=chickpea&format=deb"

Proof-of-concept lives in svn under ~/software/users/codehelp/amqp
Current version lives in svn under ~/software/trunk/packages/pybit

Useful links:
http://www.rabbitmq.com/tutorials/tutorial-one-python.html - A RabbitMQ tutorial using Python.
http://jsonpickle.github.com/
http://initd.org/psycopg/
http://www.rabbitmq.com/
http://bottlepy.org/docs/stable/index.html
http://docs.python-requests.org/en/latest/
