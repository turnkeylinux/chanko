#!/usr/bin/python
# Copyright (c) 2010 Alon Swartz <alon@turnkeylinux.org> - all rights reserved
"""
Initialize a new chanko

Arguments:
  sources.list          Path to sources.list
  trustedkeys.gpg       Path to trustedkeys.gpg used for Release verification

If sources.list and trustedkeys.gpg are specified, they will be used and chanko
will be refreshed post initialization.

If --dummy-<dist> is specified, an exemplary sources.list with matching 
trustedkeys.gpg will be created. (eg. --dummy-ubuntu, --dummy-debian)

"""
import sys
from os.path import *

import help
from chanko import Chanko

@help.usage(__doc__)
def usage():
    print >> sys.stderr, "Syntax: %s <sources.list> <trustedkeys.gpg> | --dummy-<dist>" % sys.argv[0]

def get_dummy_files(prefix):
    def f(file):
        INSTALL_PATH = dirname(dirname(__file__))
        paths = (join(INSTALL_PATH, 'contrib', file),
                 join(dirname(INSTALL_PATH), 'share/chanko/contrib', file))

        for path in paths:
            if exists(path):
                return path

        usage('could not find dummy file: ' + str(paths))

    ret = []
    for file in (prefix + '.list', prefix + '.gpg'):
        ret.append(f(file))

    return ret

def main():
    if len(sys.argv) == 2 and sys.argv[1].startswith("--dummy-"):
        prefix = sys.argv[1].replace('--dummy-', '')
        sourceslist, trustedkeys = get_dummy_files(prefix)
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
