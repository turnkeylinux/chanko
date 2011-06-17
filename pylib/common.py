
import re
import os
import md5
import hashlib

import debinfo

def mkdir(path):
    path = str(path)
    if not os.path.exists(path):
        os.makedirs(path)

def sha256sum(path):
    if os.path.exists(path):
        return hashlib.sha256(file(path, 'rb').read()).hexdigest()

    return False

def md5sum(path):
    if os.path.exists(path):
        return md5.md5(file(path, 'rb').read()).hexdigest()

    return False

def parse_inputfile(path):
    input = file(path, 'r').read().strip()

    input = re.sub(r'(?s)/\*.*?\*/', '', input) # strip c-style comments
    input = re.sub(r'//.*', '', input)

    packages = set()
    for expr in input.split('\n'):
        expr = re.sub(r'#.*', '', expr)
        expr = expr.strip()
        if not expr:
            continue

        if expr.startswith("!"):
            package = expr[1:]
        else:
            package = expr

        packages.add(package)

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
                m = re.match(r'([a-z0-9][a-z0-9\+\-\.]+)(?:\s+\((.*?)\))?$',dep)
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

