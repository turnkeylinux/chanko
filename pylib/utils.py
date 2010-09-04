# Copyright (c) 2010 Alon Swartz - all rights reserved

import os
import sys
import commands
import getpass

class Error(Exception):
    pass

def warn(s):
    print >> sys.stderr, "warning: " + str(s)

def fatal(s):
    print >> sys.stderr
    print >> sys.stderr, "FATAL: " + str(s)
    sys.exit(1)

def abort(s=None):
    if s:
        print >> sys.stderr, str(s)
    sys.exit(1)

def mkdir_parents(path, mode=0777):
    """mkdir 'path' recursively (I.e., equivalent to mkdir -p)"""
    dirs = path.split("/")
    for i in range(2, len(dirs) + 1):
        dir = "/".join(dirs[:i+1])
        if os.path.isdir(dir):
            continue
        os.mkdir(dir, mode)

def system(command, *args):
    command = command + " " + " ".join([commands.mkarg(arg) for arg in args])
    err = os.system(command)
    if err:
        raise Error("command failed: " + command,
                    os.WEXITSTATUS(err))

def getoutput(command):
    (s,o) = commands.getstatusoutput(command)
    return o

def getstatus(command):
    (s,o) = commands.getstatusoutput(command)
    return s

def join_dicts(dict1, dict2):
    for opt in dict2.keys():
        dict1[opt] = dict2[opt]
    return dict1
