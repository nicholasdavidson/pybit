#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  procmail-mbox.py
#
#  Copyright 2013 Neil Williams <codehelp@debian.org>
#  Copyright 2002 Noah Spurrier
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

#  Derived from http://code.activestate.com/recipes/157437-reading-and-writing-mbox-style-mailbox-files/

# The purpose of this file is to emulate procmail handling for a
# subscription to debian-devel-changes to help testing of the
# changes-debian hook. Pass a standard mbox as the first argument
# to the script. e.g.
# ./procmail-mbox.py mbox
# This example is hard-coded to use the changes-debian hook
# in ../hook/

import mailbox, rfc822
import sys, os, string, re
from subprocess import Popen, PIPE, STDOUT

def passthrough_filter (msg, document):
    """If you want to extend this to act as a filter
    on the changes file being parsed, simply return None here.
    msg contains the full email, with headers.
    document is just the .changes file.
    """
    return document

def process_mailbox (mailboxname_in, filter_function):
    """This processes a each message in the 'in' mailbox. Each message
    is passed to the filter_function."""
    # Open the mailbox.
    mb = mailbox.UnixMailbox (file(mailboxname_in,'r'))

    msg = mb.next()
    while msg is not None:
        # Properties of msg cannot be modified, so we pull out the
        # document to handle it separately.
        document = msg.fp.read()
        document = filter_function (msg, document)
        if document is not None:
            p = Popen(['../hook/changes-debian'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
            grep_stdout = p.communicate(input=document)[0]
            print grep_stdout
        msg = mb.next()

def main():
    mailboxname_in = sys.argv[1]
    process_mailbox (mailboxname_in, passthrough_filter)
    return 0

if __name__ == '__main__':
    main()
