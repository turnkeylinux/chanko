# Copyright (c) 2010 Alon Swartz - all rights reserved

import os
import re
import sys
import commands

from md5 import md5

class Error(Exception):
    pass

def warn(s):
    print >> sys.stderr, "warning: " + str(s)

def system(command, *args):
    command = command + " " + " ".join([commands.mkarg(arg) for arg in args])
    err = os.system(command)
    if err:
        raise Error("command failed: " + command,
                    os.WEXITSTATUS(err))

def makedirs(path):
    path = str(path)
    if not os.path.exists(path):
        os.makedirs(path)

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
    return md5(file(path, 'rb').read()).hexdigest()

