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
from plan import Plan
from utils import makedirs

from executil import getoutput

class Error(Exception):
    pass

class ChankoConfig(dict):
    def __init__(self, path):
        if not os.path.exists(path):
            raise Error("chanko config not found: " + path)

        self.required = ['release']
        self['plan_cpp'] = "" # optional
        self._parse(path)
        self._verify(self.required)

    def _parse(self, path):
        for line in file(path).readlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            key, val = line.split("=", 1)
            self[key.strip().lower()] = val.strip()

    def _verify(self, required):
        for req in self.required:
            if not self.has_key(req):
                raise Error("%s not specified in conf" % req)

            if not self[req]:
                raise Error("%s has no value in conf" % req)

    @property
    def ccurl_cache(self):
        home = os.environ.get('HOME')
        return os.path.join(home, '.ccurl/chanko', self.release)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError, e:
            raise AttributeError(e)

class Chanko(object):
    """Top-level object of the chanko"""

    def __init__(self):
        self.base = os.getcwd()
        self.config = os.path.join(self.base, 'config')
        self.architecture = getoutput("dpkg --print-architecture")

        self.trustedkeys = os.path.join(self.config, 'trustedkeys.gpg')
        self.sources_list = os.path.join(self.config, 'sources.list')
        for f in (self.sources_list, self.trustedkeys):
            if not os.path.exists(f):
                raise Error("required file not found: " + f)

        conf = ChankoConfig(os.path.join(self.config, 'chanko.conf'))
        os.environ['CCURL_CACHE'] = conf.ccurl_cache

        self.archives = os.path.join(self.base, 'archives')
        makedirs(os.path.join(self.archives, 'partial'))

        plan_path = os.path.join(self.base, 'plan')
        plan_cpp = conf.plan_cpp.replace("-", " -").strip()
        plan_cpp = plan_cpp.split(" ") if plan_cpp else []
        self.plan = Plan(plan_path, self.architecture, plan_cpp)

        self.local_cache = LocalCache(self)
        self.remote_cache = RemoteCache(self)

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

