# Copyright (c) 2010 Alon Swartz - all rights reserved

import os
import re
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
    path = str(path)
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

def list2str(list):
    lstr = ""
    for l in list:
        lstr = lstr + l + " "
    return lstr

def pretty_size(size):
    if size < 1000000:
        return "~%iKB" % (size/1024)
    else:
	return "~%iMB" % (size/(1024*1024))

def treepath(file):
    name = file.split("_")[0]
    m = re.match("^lib(.*)", name)
    if m:
        prefix = "lib" + m.group(1)[0]
    else:
        prefix = name[0]
    return prefix + "/" + name

def md5sum(path):
    return getoutput("md5sum %s | awk '{print $1}'" % path)
