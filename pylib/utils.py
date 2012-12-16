# Copyright (c) 2012 Alon Swartz <alon@turnkeylinux.org>
#
# This file is part of Chanko
#
# Chanko is free software; you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.

import os
import re

import executil
import stdtrap
import debinfo

class Error(Exception):
    pass

def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)

def format_bytes(bytes):
    G = (1024 * 1024 * 1024)
    M = (1024 * 1024)
    K = (1024)
    if bytes > G:
        return str(bytes/G) + "G"
    elif bytes > M:
        return str(bytes/M) + "M"
    else:
        return str(bytes/K) + "K"

def cpp(input, cpp_opts=[]):
    """preprocess <input> through cpp -> preprocessed output
       input may be path/to/file or iterable data type
    """
    cpp_opts.append("-Ulinux")

    command = ["cpp", input]
    command += cpp_opts

    trap = stdtrap.StdTrap()
    try:
        executil.system(*command)
    except executil.ExecError, e:
        trap.close()
        trapped_stderr = trap.stderr.read()
        raise executil.ExecError(" ".join(command), e.exitcode, trapped_stderr)

    trap.close()
    return trap.stdout.read()

def parse_inputfile(path, cpp_opts=[]):
    output = cpp(path, cpp_opts)

    packages = set()
    for expr in output.split('\n'):
        expr = re.sub(r'#.*', '', expr)
        expr = expr.strip()
        if not expr:
            continue

        packages.add(expr)

    return packages

def promote_depends(remote_cache, packages):
    """return list of packages included those promoted
    package*  # promote recommends
    package** # promote recommends + suggests
    """
    def get_depends(package, field):
        depends = []
        control = remote_cache.query(package, info=True)
        fields = debinfo.parse_control(control)
        if fields.has_key(field):
            for dep in fields[field].split(","):
                dep = dep.strip()
                m = re.match(r'([a-z0-9][a-z0-9\+\-\.]+)(?:\s+\((.*?)\))?$', dep)
                if not m:
                    raise Error("illegally formatted dependency (%s)" % dep)

                depends.append(m.group(1))
        return depends

    toget = set()
    for package in packages:
        promote = package.count("*")
        fields = []
        if promote > 0:
            fields.append("Recommends")
        if promote == 2:
            fields.append("Suggests")

        package = package.rstrip("*")
        toget.add(package)
        for field in fields:
            toget.update(get_depends(package, field))

    return toget

