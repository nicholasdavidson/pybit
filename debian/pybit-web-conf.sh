#!/bin/sh

set -e

ucf -p /etc/pybit/debian-db.sh
# postinst maintainer script for foo-mysql

# source debconf stuff
. /usr/share/debconf/confmodule
# source dbconfig-common stuff
. /usr/share/dbconfig-common/dpkg/postinst.mysql

# create an output file which ucf will watch
# (and ensure isn't recreated) until we need to do it
dbc_generate_include=perl:/etc/pybit/debian-db.pl
dbc_generate_include_owner="root:root"
dbc_generate_include_perms="600"

dbc_go foo-mysql $@
