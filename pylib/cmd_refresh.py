#!/usr/bin/python
# Copyright (c) 2010 Alon Swartz <alon@turnkeylinux.org> - all rights reserved
"""
Refresh chanko container index files and cache

Arguments:
  -r  --remote   Resynchronize remote index files and refresh remote cache
  -l  --local    Regenerate local index and refresh local cache
  -a  --all      Refresh both remote and local

"""
import sys
import container
import help

@help.usage(__doc__)
def usage():
    print >> sys.stderr, "Syntax: %s (-r | -l | -a)" % sys.argv[0]
    
def main():
    if len(sys.argv) != 2:
        usage()

    if sys.argv[1] in ('-r', '--remote'):
        remote = True
        local  = False
    
    elif sys.argv[1] in ('-l', '--local'):
        remote = False
        local  = True
    
    elif sys.argv[1] in ('-a', '--all'):
        remote = True
        local  = True
    else:
        usage()
    
    cont = container.Container()
    cont.refresh(remote, local)
    
if __name__ == "__main__":
    main()

