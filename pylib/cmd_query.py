#!/usr/bin/python
# Copyright (c) 2010 Alon Swartz - all rights reserved
"""
Query chanko

If package_glob is provided, print only those packages whose names match the 
glob otherwise, by default, print a list of all packages
    
Arguments:
  -r  --remote   Query remote packages
  -l  --local    Query local packages stored in the chanko

Options:
  --info         Print full package information
                 Incompatible with --names option
  --names        Print only the names of packages (without the package summary)
                 Incompatible with --info option
  --stats        Print statistics of the remote/local cache

"""

import sys
import getopt
from os.path import *

import help
from chanko import Chanko

@help.usage(__doc__)
def usage():
    print >> sys.stderr, "Syntax: %s (-r | -l) [-options] [package_glob]" % sys.argv[0]

def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "rl",
                                       ['remote', 'local',
                                        'info', 'names', 'stats'])

    except getopt.GetoptError, e:
        usage(e)

    kws={}
    remote = False
    local = False
    for opt, val in opts:
        if opt in ('--info', '--names', '--stats'):
            kws[opt[2:]] = True
        elif opt in ('-r', '--remote'):
            remote = True
        elif opt in ('-l', '--local'):
            local = True
        else:
            kws[opt[2:]] = val

    if len(args) == 0:
        package = None

    elif len(args) == 1:
        package = args[0]

    else:
        usage("bad number of arguments (package_glob)")

    if not remote and not local:
        usage("remote/local not specified")

    if remote:
        pkgcache = join(str(chanko.apt.remote_cache.paths), 'pkgcache.bin')
        if not exists(pkgcache):
            chanko.apt.remote_cache.refresh()

        results = chanko.apt.remote_cache.query(package, **kws)

    if local:
        results = chanko.apt.local_cache.query(package, **kws)

    print results


if __name__ == "__main__":
    main()
