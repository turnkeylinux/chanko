#!/usr/bin/python
# Copyright (c) 2012 Alon Swartz <alon@turnkeylinux.org>
#
# This file is part of Chanko
#
# Chanko is free software; you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.
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
    cache_type = None
    for opt, val in opts:
        if opt in ('--info', '--names', '--stats'):
            kws[opt[2:]] = True
        elif opt in ('-r', '--remote'):
            cache_type = 'remote'
        elif opt in ('-l', '--local'):
            cache_type = 'local'
        else:
            kws[opt[2:]] = val

    if len(args) == 0:
        package = None

    elif len(args) == 1:
        package = args[0]

    else:
        usage("bad number of arguments (package_glob)")

    if not cache_type:
        usage("--remote or --local is required")

    chanko = Chanko()
    cache = getattr(chanko, cache_type + "_cache")
    results = cache.query(package, **kws)

    if results == None:
        print "%s cache is empty" % cache_type.capitalize()
    elif results == "":
        print "No matches found"
    else:
        print results


if __name__ == "__main__":
    main()
