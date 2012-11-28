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
Upgrade chanko archives according to log

Options:
  -p --purge     Purge superceded archives
  -f --force     Dont ask for confirmation before downloading and purging

"""

import sys
import getopt

import help

import cmd_purge
from chanko import Chanko
from utils import promote_depends, format_bytes

@help.usage(__doc__)
def usage():
    print >> sys.stderr, "Syntax: %s [-options]" % sys.argv[0]
    
def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], ":fp", ['force', 'purge'])
    except getopt.GetoptError, e:
        usage(e)

    force = False
    purge = False
    for opt, val in opts:
        if opt in ('-f', '--force'):
            force = True
        elif opt in ('-p', '--purge'):
            purge = True

    chanko = Chanko()
    chanko.remote_cache.refresh()
    chanko.local_cache.refresh()

    packages = chanko.log.list()

    upgraded = False
    for metadata in packages:
        nodeps = True if metadata == "--no-deps" else False

        toget = promote_depends(chanko.remote_cache, packages[metadata])
        candidates = chanko.get_package_candidates(toget, nodeps)

        if len(candidates) == 0:
            print "Nothing to get..."
            return

        bytes = 0
        for candidate in candidates:
            bytes += candidate.bytes
            print candidate.filename

        print "Amount of packages: %i" % len(candidates)
        print "Need to get %s of archives" % format_bytes(bytes)

        if not force:
            print "Do you want to continue [y/N]?",
            if not raw_input() in ['Y', 'y']:
                print "aborted by user"
                return

        result = chanko.get_packages(candidates=candidates)
        if result:
            upgraded = True

    if upgraded and purge:
        cmd_purge.purge(chanko.paths.archives, force)
        chanko.local_cache.refresh()

if __name__ == "__main__":
    main()

