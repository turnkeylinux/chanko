#!/usr/bin/python
# Copyright (c) 2010 Alon Swartz - all rights reserved
"""
Get package(s) and their dependencies

If a specific package version is requested, get that
If a specific version is not requested, retrieve the newest version

Options:
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
        opts, args = getopt.gnu_getopt(sys.argv[1:], "", ['force'])
    except getopt.GetoptError, e:
        usage(e)

    opt_force = False
    for opt, val in opts:
        if opt == '--force':
            opt_force = True

    packages = args
    if len(packages) == 0:
        usage("no packages specified")

    cont = container.Container()
    cont.get(packages, opt_force)

    
if __name__ == "__main__":
    main()
