# Copyright (c) 2010 Alon Swartz <alon@turnkeylinux.org> - all rights reserved

import os
from os.path import *

from paths import Paths

from common import mkdir
from cache import Cache
from log import Log

def realpath(path):
    """prevent realpath from following a symlink for basename component of path"""
    if basename(path) in ('', '.', '..'):
        return os.path.realpath(path)

    return join(os.path.realpath(dirname(path)), basename(path))

class Error(Exception):
    pass

class ChankoPaths(Paths):
    def __init__(self, path):
        self.base = realpath(path)
        Paths.__init__(self, self.base, ['config', 'archives', 'log'])
        self.config = Paths(self.config, ['sources.list',
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

