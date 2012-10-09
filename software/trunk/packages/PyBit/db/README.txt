To populate or reset the database use:
$ psql --user postgres --host catbells pybit

Then do:
pybit=# \i <path to checkout>/software/trunk/packages/PyBit/db/schema.sql
pybit=# \i <path to checkout>/software/trunk/packages/PyBit/db/populate.sql

