# Copyright (c) 2012 Alon Swartz <alon@turnkeylinux.org>
#
# This file is part of Chanko
#
# Chanko is free software; you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.

import os
import re

import executil

import releases
from utils import makedirs

class Error(Exception):
    pass

class Cache(object):
    def __init__(self, chanko, type):
        self.chanko = chanko
        self.type = type

        self.base = os.path.join(self.chanko.base, '.internal')
        self.cache = os.path.join(self.base, self.type)
        self.cache_lists = os.path.join(self.cache, 'lists')
        makedirs(self.cache_lists)

        self.state = os.path.join(self.base, 'state')
        self.state_apt = os.path.join(self.state, 'apt')
        self.state_dpkg = os.path.join(self.state, 'dpkg')
        self.state_dpkg_status = os.path.join(self.state_dpkg, 'status')
        makedirs(self.state_apt)
        makedirs(self.state_dpkg)
        file(os.path.join(self.state_dpkg_status), 'w').write('')

    @property
    def options(self):
        d = { 'Dir': self.chanko.base,
              'Dir::Etc': self.chanko.config,
              'Dir::Etc::SourceList': self.sources_list,
              'Dir::Cache': self.cache,
              'Dir::Cache::Archives': self.chanko.archives,
              'Dir::State': self.state_apt,
              'Dir::State::Lists': self.cache_lists,
              'Dir::State::status': self.state_dpkg_status,
              'APT::Architecture': self.chanko.architecture }

        return " ".join(map(lambda x: "-o %s=%s" % (x[0], x[1]), d.items()))

    @property
    def has_lists(self):
        for list in os.listdir(self.cache_lists):
            list_path = os.path.join(self.cache_lists, list)
            if list_path.endswith("Packages") and os.path.getsize(list_path) > 0:
                return True

        return False

    def _cmdcache(self, arg, sort=False):
        results = executil.getoutput("apt-cache %s %s" % (self.options, arg))
        if sort:
            results = results.splitlines()
            results.sort()
            results = "\n".join(results)

        return results

    def query(self, package, info=False, names=False, stats=False):
        if not self.has_lists:
            return None

        # list all packages with short description
        if not package and not info and not names:
            results = self._cmdcache("search .", sort=True)

        # list all packages (without description)
        elif not package and not info and names:
            results = self._cmdcache("pkgnames", sort=True)

        # list full package information on all packages
        elif not package and info and not names:
            results = self._cmdcache("dumpavail")

        # list all packages with short desc that match package_glob
        elif package and not info and not names:
            results = self._cmdcache("search %s" % package, sort=True)

        # list all packages (without description) that match a package_glob
        elif package and not info and names:
            results = self._cmdcache("pkgnames %s" % package, sort=True)

        # list info on specific package
        elif package and info and not names:
            results = self._cmdcache("show %s" % package)

        else:
            return "options provided do not match a valid query"

        if stats:
            results += "\n\n" + self._cmdcache("stats")

        return results

class RemoteCache(Cache):
    """Sub-level object of the chanko for local cache"""
    def __init__(self, chanko):
        super(RemoteCache, self).__init__(chanko, 'remote')

        makedirs(os.path.join(self.cache_lists, 'partial'))
        self.sources_list = self.chanko.sources_list

    def refresh(self):
        print "Refreshing remote cache..."

        releases.refresh(self.chanko, self)
        self._cmdcache("gencaches")

class LocalCache(Cache):
    """Sub-level object of the chanko for local cache"""
    def __init__(self, chanko):
        super(LocalCache, self).__init__(chanko, 'local')

        self.sources_list = os.path.join(self.cache, 'sources.list')
        file(self.sources_list, "w").write("deb file:/// local debs")

    def refresh(self):
        print "Refreshing local cache..."

        list = "_dists_local_debs_binary-%s_Packages" % self.chanko.architecture
        list_path = os.path.join(self.cache_lists, list)

        cmd = "apt-ftparchive packages"
        cmd += " --db=%s" % os.path.join(self.cache, 'dbcache')
        cmd += " %s > %s" % (self.chanko.archives, list_path)
        executil.system(cmd)

        self._cmdcache("gencaches")

