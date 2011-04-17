#!/usr/bin/python
"""
Purge superseded chanko archives

Options:
  -f --force     Dont ask for confirmation before purging/deleting

"""

import os
import sys
import getopt
from os.path import *

from pyproject.pool.pool import PackageCache
import debversion

import help
from chanko import Chanko

@help.usage(__doc__)
def usage():
    print >> sys.stderr, "Syntax: %s [-options]" % sys.argv[0]

def purge(path, force):
    pkgcache = PackageCache(path)

    duplicates = []
    for name, amount in pkgcache.namerefs.items():
        if amount > 1:
            duplicates.append(name)

    newest = {}
    candidates = []
    for name, version in pkgcache.list():
        if name in duplicates:
            if not newest.has_key(name) or \
               debversion.compare(newest[name], version) < 0:
                newest[name] = version
            else:
                candidates.append(pkgcache.getpath(name, version))

    if len(candidates) == 0:
        print "No candidates for deletion"
        return False

    candidates.sort()
    print "Candidates for deletion:"
    for candidate in candidates:
        print "  " + basename(candidate)

    print "Amount of candidates: %i" % len(candidates)

    if not force:
        print "Do you want to continue [y/N]?",
        if not raw_input() in ['Y', 'y']:
            print "aborted by user"
            return False

    print "Deleting..."
    for candidate in candidates:
        os.remove(candidate)

    return True

def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], ":f", ['force'])
    except getopt.GetoptError, e:
        usage(e)

    opt_force = False
    for opt, val in opts:
        if opt in ('-f', '--force'):
            opt_force = True

    chanko = Chanko()
    
    if purge(chanko.paths.archives, opt_force):
        chanko.local_cache.refresh()

if __name__ == "__main__":
    main()

