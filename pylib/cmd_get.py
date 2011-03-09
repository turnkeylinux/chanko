#!/usr/bin/python
# Copyright (c) 2010 Alon Swartz - all rights reserved
"""
Get package(s) and their dependencies

If a specific package version is requested, get that
If a specific version is not requested, retrieve the newest version

Options:
  -f --force     Dont ask for confirmation before downloading

"""

import sys
import getopt
from os.path import *

import help
from chanko import Chanko

@help.usage(__doc__)
def usage():
    print >> sys.stderr, "Syntax: %s [-options] package[=version] ..." % sys.argv[0]

def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], ":f", ['force'])
    except getopt.GetoptError, e:
        usage(e)

    opt_force = False
    for opt, val in opts:
        if opt in ('-f', '--force'):
            opt_force = True

    packages = args
    if len(packages) == 0:
        usage("no packages specified")

    chanko = Chanko()

    pkgcache = join(str(chanko.remote_cache.paths), 'pkgcache.bin')
    if not exists(pkgcache):
        chanko.remote_cache.refresh()

    chanko.remote_cache.get(packages, opt_force)
    chanko.local_cache.refresh()


if __name__ == "__main__":
    main()
