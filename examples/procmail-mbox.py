#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  procmail-mbox.py
#  
#  Copyright 2013 Neil Williams <codehelp@debian.org>
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
#  

# The purpose of this file is to emulate procmail handling for a
# subscription to debian-devel-changes. Pass a standard mbox 
# as the first argument to the script. e.g.
# ./procmail-mbox.py mbox
# This example is hard-coded to use the changes-debian hook
# in ../hook/

import mailbox, rfc822
import sys, os, string, re
from subprocess import Popen, PIPE, STDOUT

def passthrough_filter (msg, document):
    """This prints the 'from' address of the message and
    returns the document unchanged.
    """
    return document

def process_mailbox (mailboxname_in, filter_function):
    """This processes a each message in the 'in' mailbox and optionally
    writes the message to the 'out' mailbox. Each message is passed to
    the  filter_function. The filter function may return None to ignore
    the message or may return the document to be saved in the 'out' mailbox.
    See passthrough_filter().
    """
    # Open the mailbox.
    mb = mailbox.UnixMailbox (file(mailboxname_in,'r'))

    msg = mb.next()
    while msg is not None:
        # Properties of msg cannot be modified, so we pull out the
        # document to handle is separately. We keep msg around to
        # keep track of headers and stuff.
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
