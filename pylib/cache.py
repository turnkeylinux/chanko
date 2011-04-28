# Copyright (c) 2010 Alon Swartz <alon@turnkeylinux.org> - all rights reserved

import os
import re
from os.path import *

import executil
from paths import Paths

from common import mkdir
from get import Get

class Error(Exception):
    pass

class StatePaths(Paths):
    def __init__(self, path):
        Paths.__init__(self, path, ['apt', 'dpkg'])
        
        self.dpkg = Paths(self.dpkg, ['status'])

class State:
    def __init__(self, path):
        self.paths = StatePaths(path)
            
        mkdir(self.paths.apt)
        mkdir(self.paths.dpkg)
        file(self.paths.dpkg.status, "w").write("")

class CacheOptions:
    def __init__(self, chanko_paths, cache, state):
        generic = {'Dir':                  chanko_paths,
                   'Dir::Etc':             chanko_paths.config,
                   'Dir::Cache::Archives': chanko_paths.archives,
                   'Dir::State':           state.apt,
                   'Dir::State::status':   state.dpkg.status
                  }
        
        remote =  {'Dir::Cache':           cache.remote,
                   'Dir::State::Lists':    cache.remote.lists,
                   'Dir::Etc::SourceList': chanko_paths.config.sources_list
                  }

        local =   {'Dir::Cache':           cache.local,
                   'Dir::State::Lists':    cache.local.lists,
                   'Dir::Etc::SourceList': cache.local.sources_list
                  }

        generic_opts = self._generate_opts(generic)
        self.remote = generic_opts + self._generate_opts(remote)
        self.local  = generic_opts + self._generate_opts(local)

    @staticmethod
    def _generate_opts(dict):
        opts = ""
        for opt in dict.keys():
            opts = opts + "-o %s=%s " % (opt, dict[opt])
        
        return opts
                  
class CachePaths(Paths):
    def __init__(self, path):
        Paths.__init__(self, path, ['local', 'remote'])
        
        self.local  = Paths(self.local,  ['lists', 'sources.list'])
        self.remote = Paths(self.remote, ['lists'])

class Cache:
    """ class for controlling chanko cache """

    def __init__(self, cache_type, cache_id, chanko_paths):
        homedir = os.environ.get("CHANKO_HOME",
                                 join(os.environ.get("HOME"), ".chanko"))

        cachepaths = CachePaths(join(homedir, 'caches', cache_id))
        mkdir(join(cachepaths.local.lists, 'partial'))
        mkdir(join(cachepaths.remote.lists,'partial'))
        paths = {'remote': cachepaths.remote,
                 'local':  cachepaths.local}
        self.cache_type = cache_type
        self.paths = paths[self.cache_type]

        self.gcache = join(homedir, 'caches', 'global')
        mkdir(self.gcache)

        self.chanko_paths = chanko_paths
        state = State(join(homedir, 'state'))

        _options = CacheOptions(chanko_paths, cachepaths, state.paths)
        options = {'remote': _options.remote,
                   'local':  _options.local}

        self.options = options[self.cache_type]

        sourceslist = "deb file:/// local debs"
        file(cachepaths.local.sources_list, "w").write(sourceslist)

        # reminder: arch
        self.local_pkgcache = join(self.paths.lists,
                                   "_dists_local_debs_binary-i386_Packages")

    def _cmdcache(self, opts, sort=False):
        results = executil.getoutput("apt-cache %s %s" % (self.options, opts))
        if sort:
            results = results.splitlines()
            results.sort()
            results = "\n".join(results)

        return results

    def get(self, packages, force=False):
        if self.cache_type is not 'remote':
            raise Error('can only get packages if cache is remote')

        get = Get(self.paths, self.chanko_paths, self.options, self.gcache)
        return get.install(packages, force)

    def refresh(self):
        if self.cache_type is 'remote':
            print "Refreshing remote cache..."
            get = Get(self.paths, self.chanko_paths, self.options, self.gcache)
            get.update()
        else:
            print "Refreshing local cache..."
            executil.system("apt-ftparchive packages %s > %s" % 
                            (self.chanko_paths.archives,
                             self.local_pkgcache))
        self._cmdcache("gencaches")

    def query(self, package, info=False, names=False, stats=False):
        if self.cache_type is 'local':
            if (not exists(self.local_pkgcache) or
                not getsize(self.local_pkgcache) > 0):

                return "chanko is empty"

        if not package and not info and not names:
            # list all packages with short description
            results = self._cmdcache("search .", sort=True)

        elif not package and not info and names:
            # list all packages (without description)
            results = self._cmdcache("pkgnames", sort=True)

        elif not package and info and not names:
            # list full package information on all packages
            results = self._cmdcache("dumpavail")

        elif package and not info and not names:
            # list all packages with short desc that match package_glob
            results = self._cmdcache("search %s" % package, sort=True)

        elif package and not info and names:
            # list all packages (without description) that match a package_glob
            results = self._cmdcache("pkgnames %s" % package, sort=True)

        elif package and info and not names:
            # list info on specific package
            results = self._cmdcache("show %s" % package)

        else:
            print "options provided do not match a valid query"

        if stats:
            results += "\n\n" + self._cmdcache("stats")

        return results

