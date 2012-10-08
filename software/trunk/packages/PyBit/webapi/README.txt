To Run:
Run web_api.py to run it.

Deps:
    * python-jsonpickle http://packages.qa.debian.org/j/jsonpickle.html
           o http://jsonpickle.github.com/
    * python-bottle http://packages.qa.debian.org/p/python-bottle.html
          o http://bottlepy.org/
    * python-psycopg2 http://packages.qa.debian.org/p/psycopg2.html

Bottle, althogh in the debian repos as python-bottle, does not depend on any external libraries. Therefore, I include bottle.py. We need this as the new route rule syntax, amongst other things, was introduced in Bottle 0.10. Debian squeeze has 0.8x

Status:
This code is currently unfinished, but right now it shows how to work the py-postgres functions, and Bottle.py, with regards to routes, setting content types, and returning HTTP status codes.

Commands:

By the way, to poke around the database: psql -U postgres -h catbells pybit
You can test using curl like: curl -i -X GET http://0.0.0.0:8080/arch
