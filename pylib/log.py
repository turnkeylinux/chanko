from os.path import *

from common import mkdir

class Error(Exception):
    pass

class Log:
    def __init__(self, path):
        self.path = str(path)

        if isfile(self.path):
            raise Error('incompatible log file, please remove: %s' % self.path)

        if not exists(self.path):
            mkdir(self.path)

    def update(self, pkgnames, metadata=""):
        for pkgname in pkgnames:
            pkgpath = join(self.path, pkgname)
            if not exists(pkgpath):
                file(pkgpath, "w").write(metadata)

    def list(self):
        packages = {}
        for pkgname in os.listdir(self.path):
            pkgpath = join(self.path, pkgname)
            if not isfile(pkgpath):
                continue

            metadata = file(pkgpath).read().strip()
            if not packages.has_key(metadata):
                packages[metadata] = []

            packages[metadata].append(pkgname)

        return packages

