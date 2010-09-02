# Copyright (c) 2010 Alon Swartz <alon@turnkeylinux.org> - all rights reserved

import os

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
                        'Dir::Cache::Archives': base + "cache/local/archives",
                        'Dir::State::Lists':    base + "cache/local/lists",
                        'Dir::Etc::SourceList': base + "cache/local/sources.list"
                       }

class Container:
    """ class for creating and controlling a chanko container """
    
    def __init__(self):
        pass
    
    @classmethod
    def init_create(cls, sourceslist, refresh):
        """ create the container on the filesystem """
        
        if not os.path.exists(sourceslist):
            raise Error("no such sources.list '%s'" % sourceslist)

        paths = ContainerPaths()
        
        if os.path.exists(paths.generic["Dir"]):
            raise Error("container already created")
        
        def mkdir(path):
            """ recursive: creates parent dirs if they don't exist """
            head, tail = os.path.split(path)
            if head and not os.path.isdir(head):
                mkdir(head)
            if tail:
                os.mkdir(path)           
            
        mkdir(paths.generic["Dir::Etc"])
        mkdir(paths.generic["Dir::State"])

        mkdir(os.path.dirname(paths.generic["Dir::State::status"]))
        file(paths.generic["Dir::State::status"], "w").write("")
        
        for path in [paths.remote, paths.local]:
            mkdir(path["Dir::Cache"])
            mkdir(path["Dir::Cache::Archives"] + "/partial")
            mkdir(path["Dir::State::Lists"]+ "/partial")

        sources = file(sourceslist).read()
        file(paths.remote["Dir::Etc::SourceList"], "w").write(sources)

        if refresh:
            print "refreshing..."
        else:
            print "chanko sources.list: " + paths.remote("Dir::Etc::SourceList")


