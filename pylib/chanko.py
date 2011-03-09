# Copyright (c) 2010 Alon Swartz <alon@turnkeylinux.org> - all rights reserved

import os
import re
import md5
import time
import shutil
from os.path import *

from paths import Paths

from common import mkdir
from cache import Cache

def realpath(path):
    """prevent realpath from following a symlink for basename component of path"""
    if basename(path) in ('', '.', '..'):
        return os.path.realpath(path)

    return join(os.path.realpath(dirname(path)), basename(path))

class Error(Exception):
    pass

class ChankoPaths(Paths):
    def __init__(self, path=None):
        if path is None:
            path = os.getenv('CHANKO_BASE', os.getcwd())

        self.base = realpath(path)
        if not self._is_arena(self.base):
            raise Error("not inside a sumo arena")

        os.environ['CHANKO_BASE'] = path

        Paths.__init__(self, self.base, ['config', 'archives'])
        self.config = Paths(self.config, ['sources.list', 'cache_id', 'arch'])

    @staticmethod
    def _is_arena(path):
        dir = realpath(path)
        while dir is not '/':
            if basename(dir) == "arena.union":
                return True

            dir, subdir = split(dir)

        return False

class Chanko:
    """ class for creating and controlling a chanko """

    @staticmethod
    def _new_cache_id(s):
        """calculates a guaranteed unique new cache_id"""
        def digest(s):
            return md5.md5(s).hexdigest()

        return digest(s + `time.time()`)

    @classmethod
    def init_create(cls, sourceslist):
        """ create the chanko on the filesystem """
        paths = ChankoPaths()

        if not exists(sourceslist):
            raise Error("no such sources.list '%s'" % sourceslist)

        for path in (paths.config, paths.archives):
            if exists(str(path)):
                raise Error("already exists", path)

        mkdir(paths.config)
        mkdir(join(paths.archives, "partial"))

        shutil.copyfile(sourceslist, paths.config.sources_list)

        cache_id = cls._new_cache_id(paths.base)
        file(paths.config.cache_id, "w").write(cache_id)

    def __init__(self):
        self.paths = ChankoPaths()

        for path in (self.paths.config, self.paths.archives):
            if not exists(str(path)):
                raise Error("does not exist", path)

        cache_id = file(self.paths.config.cache_id).read()

        self.remote_cache = Cache('remote', cache_id, self.paths)
        self.local_cache = Cache('local', cache_id, self.paths)

