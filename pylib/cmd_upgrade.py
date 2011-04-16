#!/usr/bin/python
"""
Upgrade chanko archives according to log file

Options:
  -f --force     Dont ask for confirmation before downloading

"""

import sys
import getopt
from os.path import *

import help
from common import parse_inputfile
from chanko import Chanko

@help.usage(__doc__)
def usage():
    print >> sys.stderr, "Syntax: %s [-options]" % sys.argv[0]
    
def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], ":f", ['force'])
    except getopt.GetoptError, e:
        usage(e)

    opt_force = False
    for opt, val in opts:
        if opt in ('-f', '--force'):
            opt_force = True

    chanko = Chanko()

    chanko.remote_cache.refresh()
    chanko.local_cache.refresh()

    if not exists(chanko.paths.log):
        usage("log file not found: %s" % chanko.paths.log)

    packages = parse_inputfile(chanko.paths.log)
    chanko.remote_cache.get(packages, opt_force)

if __name__ == "__main__":
    main()

