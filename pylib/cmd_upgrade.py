#!/usr/bin/python
"""
Upgrade chanko archives according to log

Options:
  -p --purge     Purge superceded archives
  -f --force     Dont ask for confirmation before downloading and purging
  -n --nodeps    Do not get package dependencies

"""

import sys
import getopt
from os.path import *

import help
from cmd_purge import purge
from chanko import Chanko
from common import promote_depends

@help.usage(__doc__)
def usage():
    print >> sys.stderr, "Syntax: %s [-options]" % sys.argv[0]
    
def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], ":fpn", 
                                       ['force', 'purge', 'nodeps'])
    except getopt.GetoptError, e:
        usage(e)

    opt_force = False
    opt_purge = False
    opt_nodeps = False
    for opt, val in opts:
        if opt in ('-f', '--force'):
            opt_force = True
        elif opt in ('-p', '--purge'):
            opt_purge = True
        elif opt in ('-n', '--nodeps'):
            opt_nodeps = True

    chanko = Chanko()

    chanko.remote_cache.refresh()
    chanko.local_cache.refresh()

    toget = promote_depends(chanko.remote_cache, chanko.log.list())
    if chanko.remote_cache.get(toget, opt_force, nodeps=opt_nodeps):
        if opt_purge:
            purge(chanko.paths.archives, opt_force)

        chanko.local_cache.refresh()


if __name__ == "__main__":
    main()

