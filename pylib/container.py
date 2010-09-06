# Copyright (c) 2010 Alon Swartz <alon@turnkeylinux.org> - all rights reserved

import os
import re
import shutil
import random
import commands
from os.path import *

from utils import *
from paths import Paths
from apt import Apt

def realpath(path):
    """prevent realpath from following a symlink for basename component of path"""
    if basename(path) in ('', '.', '..'):
        return os.path.realpath(path)

    return join(os.path.realpath(dirname(path)), basename(path))

def randomkey():
    return str(random.randint(100000000000, 999999999999))
    
class ContainerPaths(Paths):
    def __init__(self, path=None):
        if path is None:
            path = os.getenv('CHANKO_BASE', os.getcwd())

        self.chanko_base = path
        
        path = realpath(path)
        self.base = join(path, ".container/")

        Paths.__init__(self, self.base, ['config', 'archives'])
        self.config = Paths(self.config, ['sources.list', 'hash', 'arch'])

class Container:
    """ class for creating and controlling a chanko container """

    def init_create(self, sourceslist, refresh):
        """ create the container on the filesystem """
        
        if not exists(sourceslist):
            fatal("no such sources.list '%s'" % sourceslist)

        if exists(self.paths.base):
            fatal("container already exists: " + self.paths.base)

        mkdir_parents(self.paths.config)
        mkdir_parents(join(self.paths.archives, "partial"))

        shutil.copyfile(sourceslist, self.paths.config.sources_list)
        
        file(self.paths.config.hash, "w").write(randomkey())
        
        if refresh:
            self.apt = Apt(self.paths, create=True)
            self.refresh(remote=True, local=False)
        else:
            print "chanko sources.list: " + self.paths.config.sources_list

    def __init__(self, create=False):
        self.paths = ContainerPaths()
        if not isdir(self.paths.base) and not create:
            fatal("chanko container does not exist: " + self.paths.base)
        
        if not create:
            self.apt = Apt(self.paths)

    def refresh(self, remote, local):
        if remote:
            self.apt.remote_cache.refresh()
        
        if local:
            self.apt.local_cache.refresh()
            
    def query(self, remote, local, package, info=False, names=False, stats=False):
        if remote:
            self.apt.remote_cache.query(package, info, names, stats)
        
        if local:
            self.apt.local_cache.query(package, info, names, stats)

    def get(self, packages, dir="", tree=False, force=False):
        if re.match("^/(.*)", dir):
            fatal("absolute paths are not allowed: " + dir)
            
        dir = join(self.paths.chanko_base, dir)
        
        self.apt.get.install(packages, dir, tree, force)
        self.apt.local_cache.refresh()

        
