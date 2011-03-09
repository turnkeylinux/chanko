# Copyright (c) 2010 Alon Swartz <alon@turnkeylinux.org> - all rights reserved

import os
import re
import shutil
import random

from os.path import *

from paths import Paths
from apt import Apt

def realpath(path):
    """prevent realpath from following a symlink for basename component of path"""
    if basename(path) in ('', '.', '..'):
        return os.path.realpath(path)

    return join(os.path.realpath(dirname(path)), basename(path))

def randomkey():
    return str(random.randint(100000000000, 999999999999))

def makedirs(path):
    path = str(path)
    if not os.path.exists(path):
        os.makedirs(path)

class Error(Exception):
    pass

class ContainerPaths(Paths):
    def __init__(self, path=None):
        if path is None:
            path = os.getenv('CHANKO_BASE', os.getcwd())

        self.base = realpath(path)
        if not self._is_arena(self.base):
            raise Error("not inside a sumo arena")

        os.environ['CHANKO_BASE'] = path

        Paths.__init__(self, self.base, ['config', 'archives'])
        self.config = Paths(self.config, ['sources.list', 'hash', 'arch'])

    @staticmethod
    def _is_arena(path):
        dir = realpath(path)
        while dir is not '/':
            if basename(dir) == "arena.union":
                return True

            dir, subdir = split(dir)

        return False

class Container:
    """ class for creating and controlling a chanko container """

    @classmethod
    def init_create(cls, sourceslist):
        """ create the container on the filesystem """
        paths = ContainerPaths()
        
        if not exists(sourceslist):
            raise Error("no such sources.list '%s'" % sourceslist)

        for path in (paths.config, paths.archives):
            if exists(str(path)):
                raise Error("already exists", path)

        makedirs(paths.config)
        makedirs(join(paths.archives, "partial"))

        shutil.copyfile(sourceslist, paths.config.sources_list)
        
        file(paths.config.hash, "w").write(randomkey())
        
    def __init__(self):
        self.paths = ContainerPaths()
        
        for path in (self.paths.config, self.paths.archives):
            if not exists(str(path)):
                raise Error("does not exist", path)

        self.apt = Apt(self.paths)

    def refresh(self, remote, local):
        if remote:
            self.apt.remote_cache.refresh()
        
        if local:
            self.apt.local_cache.refresh()
            
    def query(self, remote, local, package, info=False, names=False, stats=False):
        if remote:
            if not exists(join(str(self.apt.remote_cache.paths), 'pkgcache.bin')):
                self.apt.remote_cache.refresh()

            return self.apt.remote_cache.query(package, info, names, stats)
        
        if local:
            return self.apt.local_cache.query(package, info, names, stats)

    def get(self, packages, dir="", tree=False, force=False):
        if re.match("^/(.*)", dir):
            raise("absolute paths are not allowed: " + dir)
            
        dir = join(self.paths.base, dir)

        if self.apt.get.install(packages, dir, tree, force):
            self.apt.local_cache.refresh()


