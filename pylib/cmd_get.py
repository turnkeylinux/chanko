#!/usr/bin/python
"""
Get package(s) and their dependencies

Arguments:
  <packages> := ( path/to/inputfile | package[=version] ) ...
                If a version isn't specified, the newest version is implied.

Options:
  -f --force     Dont ask for confirmation before downloading

"""

import sys
import getopt
from os.path import *

import help
from common import parse_inputfile
from chanko import Chanko

@help.usage(__doc__)
def usage():
    print >> sys.stderr, "Syntax: %s [-options] <packages>" % sys.argv[0]

def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], ":f", ['force'])
    except getopt.GetoptError, e:
        usage(e)

    opt_force = False
    for opt, val in opts:
        if opt in ('-f', '--force'):
            opt_force = True

    if len(args) == 0:
        usage("bad number of arguments")

    packages = set()
    for arg in args:
        if exists(arg):
            packages.update(parse_inputfile(arg))
        else:
            packages.add(arg)

    chanko = Chanko()

    pkgcache = join(str(chanko.remote_cache.paths), 'pkgcache.bin')
    if not exists(pkgcache):
        chanko.remote_cache.refresh()

    if chanko.remote_cache.get(packages, opt_force):
        chanko.local_cache.refresh()
        chanko.log.update(packages)


if __name__ == "__main__":
    main()
