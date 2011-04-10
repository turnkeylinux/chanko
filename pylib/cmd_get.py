#!/usr/bin/python
"""
Get package(s) and their dependencies

Arguments:
  <packages> := ( path/to/inputfile | package[=version] ) ...
                If a version isn't specified, the newest version is implied.

Options:
  -f --force     Dont ask for confirmation before downloading

"""

import re
import sys
import getopt
from os.path import *

import help
from chanko import Chanko

@help.usage(__doc__)
def usage():
    print >> sys.stderr, "Syntax: %s [-options] <packages>" % sys.argv[0]

def parse_inputfile(path):
    input = file(path, 'r').read().strip()

    input = re.sub(r'(?s)/\*.*?\*/', '', input) # strip c-style comments
    input = re.sub(r'//.*', '', input)

    packages = set()
    for expr in input.split('\n'):
        expr = re.sub(r'#.*', '', expr)
        expr = expr.strip()
        expr = expr.rstrip("*")
        if not expr:
            continue

        if expr.startswith("!"):
            package = expr[1:]
        else:
            package = expr

        packages.add(package)

    return packages


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

    chanko.remote_cache.get(packages, opt_force)
    chanko.local_cache.refresh()


if __name__ == "__main__":
    main()
