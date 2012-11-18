# Copyright (c) 2010 Alon Swartz <alon@turnkeylinux.org> - all rights reserved

import os
import re
import time
import shutil
from hashlib import md5
from os.path import *

from paths import Paths

from common import mkdir, md5sum
from cache import Cache

def realpath(path):
    """prevent realpath from following a symlink for basename component of path"""
    if basename(path) in ('', '.', '..'):
        return os.path.realpath(path)

    return join(os.path.realpath(dirname(path)), basename(path))

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

class ChankoPaths(Paths):
    def __init__(self, path=None):
        if path is None:
            path = os.getenv('CHANKO_BASE', os.getcwd())

        self.base = realpath(path)
        os.environ['CHANKO_BASE'] = path

        Paths.__init__(self, self.base, ['config', 'archives', 'log'])
        self.config = Paths(self.config, ['sources.list',
                                          'sources.list.md5',
                                          'cache_id',
                                          'blacklist',
                                          'trustedkeys.gpg',
                                          'arch'])

class Chanko:
    """ class for creating and controlling a chanko """

    @staticmethod
    def _new_cache_id(s):
        """calculates a guaranteed unique new cache_id"""
        def digest(s):
            return md5(s).hexdigest()

        return digest(s + `time.time()`)

    @classmethod
    def init_create(cls, sourceslist, trustedkeys):
        """ create the chanko on the filesystem """
        paths = ChankoPaths()

        for path in (sourceslist, trustedkeys):
            if not exists(path):
                raise Error("does not exist: %s" % path)

        for path in (paths.config, paths.archives, paths.log):
            if exists(str(path)):
                raise Error("already exists", path)

        mkdir(paths.config)
        mkdir(join(paths.archives, "partial"))
        Log(paths.log) # initialize log

        shutil.copyfile(sourceslist, paths.config.sources_list)
        shutil.copyfile(trustedkeys, paths.config.trustedkeys_gpg)

        checksum = md5sum(paths.config.sources_list)
        file(paths.config.sources_list_md5, "w").write(checksum)

        cache_id = cls._new_cache_id(paths.base)
        file(paths.config.cache_id, "w").write(cache_id)

    def __init__(self):
        self.paths = ChankoPaths()

        for path in (self.paths.config, self.paths.archives):
            if not exists(str(path)):
                raise Error("chanko path not found: ", path)

        mkdir(join(self.paths.archives, "partial"))
        cache_id = file(self.paths.config.cache_id).read().strip()

        self.remote_cache = Cache('remote', cache_id, self.paths)
        self.local_cache = Cache('local', cache_id, self.paths)
        self.log = Log(self.paths.log)

        self.remote_cache_auto_refreshed = False
        self._sources_list_updated()

    def _sources_list_updated(self):
        current_checksum = md5sum(self.paths.config.sources_list)
        if exists(self.paths.config.sources_list_md5):
            expected_checksum = file(self.paths.config.sources_list_md5).read().strip()
        else:
            expected_checksum = ""

        if current_checksum != expected_checksum:
            self.remote_cache.refresh()
            self.remote_cache_auto_refreshed = True
            file(self.paths.config.sources_list_md5, "w").write(current_checksum)

