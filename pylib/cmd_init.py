#!/usr/bin/python
# Copyright (c) 2010 Alon Swartz <alon@turnkeylinux.org> - all rights reserved
"""
Initialize a new chanko container

If sources.list is specified, it will be used and the container will be
refreshed post initialization.

If --dummy is specified, an exemplary sources.list will be created.

"""
import sys
import container
import help

@help.usage(__doc__)
def usage():
    print >> sys.stderr, "Syntax: %s /path/to/sources.list | --dummy" % sys.argv[0]
    
def main():
    if len(sys.argv) != 2:
        usage()

    if sys.argv[1] == "--dummy":
        sourceslist = "/usr/share/chanko/sources.list"
        refresh = False
    else:
        sourceslist = sys.argv[1]
        refresh = True

    container.Container.init_create(sourceslist, refresh)
    
if __name__ == "__main__":
    main()
