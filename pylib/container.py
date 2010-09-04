# Copyright (c) 2010 Alon Swartz <alon@turnkeylinux.org> - all rights reserved

import os
import re
import string
import commands
from os.path import *

from utils import *
import apt

class ContainerPaths:
    def __init__(self, path=None):
        if path is None:
            path = os.getenv('CHANKO_DIR', os.getcwd())

        self.path = realpath(path)
        base = self.path + "/.chanko/"

        self.generic = {'Dir':                  base,
                        'Dir::Etc':             base + "config/",
                        'Dir::State':           base + "state/apt",
                        'Dir::State::status':   base + "state/dpkg/status"
                       }
        
        self.remote =  {'Dir::Cache':           base + "cache/remote",
                        'Dir::Cache::Archives': base + "cache/remote/archives",
                        'Dir::State::Lists':    base + "cache/remote/lists",
                        'Dir::Etc::SourceList': base + "config/sources.list"
                       }

        self.local =   {'Dir::Cache':           base + "cache/local",
                        'Dir::Cache::Archives': base + "cache/remote/archives",
                        'Dir::State::Lists':    base + "cache/local/lists",
                        'Dir::Etc::SourceList': base + "cache/local/sources.list"
                       }
        
        generic_opts = self._generate_opts(self.generic)
        self.remote_opts = generic_opts + self._generate_opts(self.remote)
        self.local_opts  = generic_opts + self._generate_opts(self.local)
    
    def _generate_opts(self, dict):
        opts = ""
        for opt in dict.keys():
            opts = opts + "-o %s=%s " % (opt, dict[opt])
        
        return opts

class Container:
    """ class for creating and controlling a chanko container """
    
    def __init__(self):
        self.paths = ContainerPaths()
    
    def init_create(self, sourceslist, refresh):
        """ create the container on the filesystem """
        
        if not exists(sourceslist):
            raise Error("no such sources.list '%s'" % sourceslist)
        
        if exists(self.paths.generic["Dir"]):
            raise Error("container already created")
        
        mkdir_parents(self.paths.generic["Dir::Etc"])
        mkdir_parents(self.paths.generic["Dir::State"])

        mkdir_parents(dirname(self.paths.generic["Dir::State::status"]))
        file(self.paths.generic["Dir::State::status"], "w").write("")
        
        for path in [self.paths.remote, self.paths.local]:
            mkdir_parents(path["Dir::Cache"])
            mkdir_parents(path["Dir::Cache::Archives"] + "/partial")
            mkdir_parents(path["Dir::State::Lists"]+ "/partial")

        r_sources = file(sourceslist).read()
        file(self.paths.remote["Dir::Etc::SourceList"], "w").write(r_sources)
        
        l_sources = "deb file:/// local debs"
        file(self.paths.local["Dir::Etc::SourceList"], "w").write(l_sources)

        if refresh:
            self.refresh(remote=True, local=False)
        else:
            print "chanko sources.list: " + self.paths.remote("Dir::Etc::SourceList")

    def _join_dicts(self, dict1, dict2):
        for opt in dict2.keys():
            dict1[opt] = dict2[opt]                
        return dict1
    
    def _remote_get(self):
        paths = self._join_dicts(self.paths.generic, self.paths.remote)
        return apt.Get(paths, self.paths.remote_opts)

    def _remote_cache(self):
        paths = self._join_dicts(self.paths.generic, self.paths.remote)
        return apt.Cache(paths, self.paths.remote_opts)

    def _local_cache(self):
        paths = self._join_dicts(self.paths.generic, self.paths.local)
        return apt.Cache(paths, self.paths.local_opts)

    def refresh(self, remote, local):
        """ resynchronize remote / refresh local index files and caches """

        if not exists(self.paths.generic["Dir"]):
            raise Error("chanko container does not exist")
        
        if remote:
            cache = self._remote_cache()
            cache.refresh()
        
        if local:
            cache = self._local_cache()
            cache.refresh()
            
    def query(self, remote, local, package, 
              info=False, names=False, stats=False):

        if remote:
            cache = self._remote_cache()
            cache.query(package, info, names, stats)
        
        if local:
            pkg_cache = self.paths.local["Dir::State::Lists"] + "/_dists_local_debs_binary-i386_Packages"
            if exists(pkg_cache) and getsize(pkg_cache) > 0:
                cache = self._local_cache()
                cache.query(package, info, names, stats)
            else:
                print "container empty"

    def get(self, packages, dir=None, tree=False, force=False):
        if not dir:
            dir = self.paths.path
        get = self._remote_get()
        get.install(packages, dir, tree, force)
        
        #refresh local cache so it can be queried
        self.refresh(remote=False, local=True)
        
