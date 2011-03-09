#!/usr/bin/python
# Copyright (c) 2010 Alon Swartz <alon@turnkeylinux.org> - all rights reserved
"""
Initialize a new chanko

If sources.list is specified, it will be used and chanko will be refreshed
post initialization.

If --dummy is specified, an exemplary sources.list will be created.

"""
import sys
from os.path import *

import help
from chanko import Chanko

@help.usage(__doc__)
def usage():
    print >> sys.stderr, "Syntax: %s /path/to/sources.list | --dummy" % sys.argv[0]

def get_dummy_sourceslist():
    INSTALL_PATH = dirname(dirname(__file__))
    
    paths = (join(INSTALL_PATH, 'contrib/sources.list'),
             join(dirname(INSTALL_PATH), 'share/chanko/contrib/sources.list'))

    for path in paths:
        if exists(path):
            return path

    usage('dummy sources.list file not found: ' + paths)

def main():
    if len(sys.argv) != 2:
        usage()

    if sys.argv[1] == "--dummy":
        sourceslist = get_dummy_sourceslist()
        refresh = False
    else:
        sourceslist = sys.argv[1]
        refresh = True

    Chanko.init_create(sourceslist)
    if refresh:
        chanko = Chanko()
        if not chanko.remote_cache_auto_refreshed:
            chanko.remote_cache.refresh()

if __name__ == "__main__":
    main()
