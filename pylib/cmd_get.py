#!/usr/bin/python
# Copyright (c) 2010 Alon Swartz - all rights reserved
"""
Get package(s) and their dependencies

If a specific package version is requested, get that
If a specific version is not requested, retrieve the newest version

Options:
  --dir=         Relative directory path to CHANKO_BASE for package storage
                 Default is CHANKO_BASE
  --force        Dont ask for confirmation before downloading

"""

import re
import sys
import getopt
import container
import help

@help.usage(__doc__)
def usage():
    print >> sys.stderr, "Syntax: %s [-options] package[=version] ..." % sys.argv[0]

def warn(s):
    print >> sys.stderr, "warning: " + str(s)

def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "",
                                       ['dir=', 'force'])

    except getopt.GetoptError, e:
        usage(e)

    kws={}
    remote = False
    local = False
    for opt, val in opts:
        if opt in ('--force'):
            kws[opt[2:]] = True
        else:
            kws[opt[2:]] = val
    
    if len(args) == 0:
        usage("no packages specified")

    cont = container.Container()
    cont.get(args, **kws)

    
if __name__ == "__main__":
    main()
