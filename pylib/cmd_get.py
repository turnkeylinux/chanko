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
Get package(s) and their dependencies

Arguments:
  <packages> := ( path/to/inputfile | package[=version] ) ...
                If a version isn't specified, the newest version is implied.

Options:
  -p --pretend   Displays which packages would be downloaded
  -f --force     Do not ask for confirmation before downloading
  -n --no-deps   Do not get package dependencies

"""

import os
import sys
import getopt

import help
from utils import parse_inputfile, format_bytes
from chanko import get_chankos

@help.usage(__doc__)
def usage():
    print >> sys.stderr, "Syntax: %s [-options] <packages>" % sys.argv[0]

def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], ":fpn",
                                       ['force', 'pretend', 'no-deps'])
    except getopt.GetoptError, e:
        usage(e)

    force = False
    nodeps = False
    pretend = False
    for opt, val in opts:
        if opt in ('-f', '--force'):
            force = True
        elif opt in ('-p', '--pretend'):
            pretend = True
        elif opt in ('-n', '--no-deps'):
            nodeps = True

    if len(args) == 0:
        usage()

    if force and pretend:
        usage("conflicting options: --force, --pretend")

    packages = set()
    for arg in args:
        if os.path.exists(arg):
            packages.update(parse_inputfile(arg))
        else:
            packages.add(arg)

    for chanko in get_chankos():
        candidates = chanko.get_package_candidates(packages, nodeps)

        if len(candidates) == 0:
            print "Nothing to get..."
            continue

        bytes = 0
        for candidate in candidates:
            bytes += candidate.bytes
            print candidate.filename

        print "Amount of packages: %i" % len(candidates)
        print "Need to get %s of archives" % format_bytes(bytes)

        if pretend:
            continue

        if not force:
            print "Do you want to continue [y/N]?",
            if not raw_input() in ['Y', 'y']:
                print "aborted by user"
                continue

        result = chanko.get_packages(candidates=candidates)
        if result:
            plan_name = "nodeps" if nodeps else "main"
            chanko.plan.update(packages, plan_name)


if __name__ == "__main__":
    main()

