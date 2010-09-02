# Copyright (c) 2010 Alon Swartz <alon@turnkeylinux.org> - all rights reserved

import os
import re
import string
import commands

import cache

class Error(Exception):
    pass

class ContainerPaths:
    def __init__(self, path=None):
        if path is None:
            path = os.getenv('CHANKO_DIR', os.getcwd())

        path = os.path.realpath(path)
        base = path + "/.chanko/"

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
        
        if not os.path.exists(sourceslist):
            raise Error("no such sources.list '%s'" % sourceslist)
        
        if os.path.exists(self.paths.generic["Dir"]):
            raise Error("container already created")
        
        def mkdir(path):
            """ recursive: creates parent dirs if they don't exist """
            head, tail = os.path.split(path)
            if head and not os.path.isdir(head):
                mkdir(head)
            if tail:
                os.mkdir(path)           
            
        mkdir(self.paths.generic["Dir::Etc"])
        mkdir(self.paths.generic["Dir::State"])

        mkdir(os.path.dirname(paths.generic["Dir::State::status"]))
        file(self.paths.generic["Dir::State::status"], "w").write("")
        
        for path in [self.paths.remote, self.paths.local]:
            mkdir(path["Dir::Cache"])
            mkdir(path["Dir::Cache::Archives"] + "/partial")
            mkdir(path["Dir::State::Lists"]+ "/partial")

        r_sources = file(sourceslist).read()
        file(self.paths.remote["Dir::Etc::SourceList"], "w").write(r_sources)
        
        l_sources = "deb file:/// local debs"
        file(self.paths.local["Dir::Etc::SourceList"], "w").write(l_sources)

        if refresh:
            print "refreshing..."
            self.refresh(remote=True, local=False)
        else:
            print "chanko sources.list: " + self.paths.remote("Dir::Etc::SourceList")

    def refresh(self, remote, local):
        """ resynchronize remote / refresh local index files and caches """

        if not os.path.exists(self.paths.generic["Dir"]):
            raise Error("chanko container does not exist")
        
        def _join_dicts(dict1, dict2):
            for opt in dict2.keys():
                dict1[opt] = dict2[opt]                
            return dict1

        if remote:
            paths = _join_dicts(self.paths.generic, self.paths.remote)
            c = cache.Cache(paths, self.paths.remote_opts)
            c.refresh()
        
        if local:
            paths = _join_dicts(self.paths.generic, self.paths.local)
            c = cache.Cache(paths, self.paths.local_opts)
            c.refresh()
            

