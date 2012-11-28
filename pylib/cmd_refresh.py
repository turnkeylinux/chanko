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
Refresh chanko index files and cache

Arguments:
  -r  --remote   Resynchronize remote index files and refresh remote cache
  -l  --local    Regenerate local index and refresh local cache
  -a  --all      Refresh both remote and local

"""
import sys

import help
from chanko import Chanko

@help.usage(__doc__)
def usage():
    print >> sys.stderr, "Syntax: %s (-r | -l | -a)" % sys.argv[0]
    
def main():
    if len(sys.argv) != 2:
        usage()

    local = False
    remote = False

    if sys.argv[1] in ('-r', '--remote'):
        remote = True
    
    elif sys.argv[1] in ('-l', '--local'):
        local  = True
    
    elif sys.argv[1] in ('-a', '--all'):
        remote = True
        local  = True
    else:
        usage()
    
    chanko = Chanko()
    if remote:
        chanko.remote_cache.refresh()
    
    if local:
        chanko.local_cache.refresh()

if __name__ == "__main__":
    main()

