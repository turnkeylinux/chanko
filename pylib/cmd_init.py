#!/usr/bin/python
# Copyright (c) 2010 Alon Swartz <alon@turnkeylinux.org> - all rights reserved
"""
Initialize a new chanko

Arguments:
  sources.list          Path to sources.list
  trustedkeys.gpg       Path to trustedkeys.gpg used for Release verification

If sources.list and trustedkeys.gpg are specified, they will be used and chanko
will be refreshed post initialization.

If --dummy is specified, an exemplary sources.list with matching trustedkeys.gpg
will be created.

"""
import sys
from os.path import *

import help
from chanko import Chanko

@help.usage(__doc__)
def usage():
    print >> sys.stderr, "Syntax: %s <sources.list> <trustedkeys.gpg> | --dummy" % sys.argv[0]

def get_dummy_files():
    def f(file):
        INSTALL_PATH = dirname(dirname(__file__))
        paths = (join(INSTALL_PATH, 'contrib', file),
                 join(dirname(INSTALL_PATH), 'share/chanko/contrib', file))

        for path in paths:
            if exists(path):
                return path

        usage('could not find \'%s\' in: ' + paths)

    ret = []
    for file in ('sources.list', 'trustedkeys.gpg'):
        ret.append(f(file))

    return ret

def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--dummy":
        sourceslist, trustedkeys = get_dummy_files()
        refresh = False

    elif len(sys.argv) == 3:
        sourceslist = sys.argv[1]
        trustedkeys = sys.argv[2]
        refresh = True

    else:
        usage("bad number of arguments")

    Chanko.init_create(sourceslist, trustedkeys)
    if refresh:
        chanko = Chanko()
        if not chanko.remote_cache_auto_refreshed:
            chanko.remote_cache.refresh()

if __name__ == "__main__":
    main()
