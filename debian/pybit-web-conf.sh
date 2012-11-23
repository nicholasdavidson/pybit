# shell snippet to get the dbconfig values for pybit-web
# as there is no perl binding for dbconfig.
# Used by pybit-web.postinst
# idempotency - this is an intermediate file only.
ucf -p /etc/pybit/debian-db.sh
# source debconf stuff
. /usr/share/debconf/confmodule
# source dbconfig-common stuff
. /usr/share/dbconfig-common/dpkg/postinst.pgsql

# create an output file which ucf will watch
# (and ensure isn't recreated) until we need to do it
dbc_generate_include=perl:/etc/pybit/debian-db.pl
# minimal permissions
dbc_generate_include_owner="root:root"
dbc_generate_include_perms="600"
dbc_go pybit-web $@
