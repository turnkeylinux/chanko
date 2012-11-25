# Copyright (c) 2010 Alon Swartz <alon@turnkeylinux.org> - all rights reserved

import os
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
    def __init__(self, path):
        self.base = realpath(path)
        Paths.__init__(self, self.base, ['config', 'archives', 'log'])
        self.config = Paths(self.config, ['sources.list',
                                          'sources.list.md5',
                                          'blacklist',
                                          'trustedkeys.gpg',
                                          'arch'])

class Chanko:
    """ class for controlling a chanko """

    def __init__(self):
        self.paths = ChankoPaths(os.getcwd())

        for f in (self.paths.config.sources_list, self.paths.config.trustedkeys_gpg):
            if not exists(f):
                raise Error("chanko path not found: ", f)

        mkdir(join(self.paths.archives, "partial"))
        self.remote_cache = Cache('remote', self.paths)
        self.local_cache = Cache('local', self.paths)
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

