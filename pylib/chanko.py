# Copyright (c) 2012 Alon Swartz <alon@turnkeylinux.org>
#
# This file is part of Chanko
#
# Chanko is free software; you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.

import os

from cache import RemoteCache, LocalCache
from packages import get_uris, download_uris
from log import Log
from utils import makedirs

class Error(Exception):
    pass

class Chanko(object):
    """Top-level object of the chanko"""

    def __init__(self):
        self.base = os.getcwd()
        self.config = os.path.join(self.base, 'config')
        self.trustedkeys = os.path.join(self.config, 'trustedkeys.gpg')
        self.sources_list = os.path.join(self.config, 'sources.list')
        arch_path = os.path.join(self.config, 'arch')

        for f in (self.sources_list, self.trustedkeys, arch_path):
            if not os.path.exists(f):
                raise Error("required file not found: " + f)

        self.architecture = file(arch_path).read().strip()
        if not self.architecture:
            raise Error("architecture is not defined: " + arch_path)

        self.archives = os.path.join(self.base, 'archives')
        makedirs(os.path.join(self.archives, 'partial'))

        self.local_cache = LocalCache(self)
        self.remote_cache = RemoteCache(self)

        self.log = Log(os.path.join(self.base, 'log'))

    def get_package_candidates(self, packages, nodeps=False):
        if not self.remote_cache.has_lists:
            self.remote_cache.refresh()

        return get_uris(self, self.remote_cache, packages, nodeps)

    def get_packages(self, candidates=None, packages=None, nodeps=False):
        if packages:
            candidates = self.get_package_candidates(packages, nodeps)

        if not candidates:
            return False

        result = download_uris(candidates)
        if result:
            self.local_cache.refresh()

        return result

