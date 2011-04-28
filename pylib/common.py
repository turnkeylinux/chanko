
import re
import os
import md5

def mkdir(path):
    path = str(path)
    if not os.path.exists(path):
        os.makedirs(path)

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
        expr = expr.rstrip("*")
        if not expr:
            continue

        if expr.startswith("!"):
            package = expr[1:]
        else:
            package = expr

        packages.add(package)

    return packages
