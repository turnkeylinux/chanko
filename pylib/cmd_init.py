#!/usr/bin/python
# Copyright (c) 2010 Alon Swartz <alon@turnkeylinux.org> - all rights reserved
"""
Initialize a new chanko container

If sources.list is specified, it will be used and the container will be
refreshed post initialization.

If --dummy is specified, an exemplary sources.list will be created.

"""
import sys
from os.path import *

import container
import help

class Error(Exception):
    pass

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

    raise Error('dummy sources.list file not found', paths)

def main():
    if len(sys.argv) != 2:
        usage()

    if sys.argv[1] == "--dummy":
        sourceslist = get_dummy_sourceslist()
        refresh = False
    else:
        sourceslist = sys.argv[1]
        refresh = True

    container.Container.init_create(sourceslist)
    if refresh:
        cont = container.Container()
        cont.refresh(remote=True, local=False)


if __name__ == "__main__":
    main()
