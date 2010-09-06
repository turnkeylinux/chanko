# Copyright (c) 2010 Alon Swartz <alon@turnkeylinux.org> - all rights reserved

import os
import re
import errno
from os.path import *

from utils import *
from paths import Paths

class Uri:
    def __init__(self, url):
        self.url = url
        self.filename = basename(url)
        self.destfile = None
        self.tree = treepath(self.filename)
        self.path = None
        self.md5 = None
        self.size = 0

    def _sumocmd(self, opts):
        # CHANKO_BASE _should be_ equivalent to SUMO_BASE
        # currently we have to chdir into SUMO_BASE, setting env doesn't work
        cwd = os.getcwd()
        os.chdir(os.getenv('CHANKO_BASE', cwd))
        system("sumo-" + opts)
        os.chdir(cwd)
        
    def set_path(self, dir, tree=False):
        if not dir:
            raise Error("dir not passed for: " + self.url)
        
        if self.destfile:
            filename = self.destfile
        else:
            filename = self.filename
        
        if tree:
            self.path = join(dir, self.tree, filename)
        else:
            self.path = join(dir, filename)

    def get(self, dir=None, tree=False):
        if not self.path:
            self.set_path(dir, tree)

        print "* get: " + basename(self.path)
        if re.match("(.*).deb", self.path):
            self._sumocmd("get %s %s" % (self.url, self.path))
        else:
            system("curl -L -f %s -o %s" % (self.url, self.path))

    def md5_verify(self):
        if not self.path:
            fatal("no path set for: " + self.filename)
        
        if not self.md5:
            fatal("no md5 set for: " + self.path)

        if not self.md5 == md5sum(self.path):
            fatal("md5sum verification failed: %s" % self.path)
        
    def archive(self, archive_path):
        dest = join(archive_path, self.filename)
        self._sumocmd("cp -l %s %s" % (self.path, dest))

class Get:
    def __init__(self, paths, options, archives):
        self.paths = paths
        self.options = options
        self.archives = archives

    def _cmdget(self, opts):
        return getoutput("apt-get %s --print-uris %s" % (self.options, opts))
    
    def _parse_update_uris(self, raw):
        self.uris = []
        for uri in raw.split("\n"):
            m = re.match("\'(.*)\' (.*) 0", uri)
            if m:
                if not re.match("(.*)Translation(.*)", m.group(1)):
                    uri = Uri(m.group(1))
                    uri.destfile = m.group(2)

                    self.uris.append(uri)

    def _parse_install_uris(self, raw):
        self.uris = []
        for line in raw.split("\n"):
            if re.match("Need to get 0B(.*)", line):
                abort("Newest version already in container")
            
            m = re.match("\'(.*)\' (.*) (.*) (.*)", line)
            if m:
                uri = Uri(m.group(1))
                uri.size = int(m.group(3))
                uri.md5 = m.group(4)
                
                self.uris.append(uri)
    
    def update(self):
        raw = self._cmdget("update")
        uris = self._parse_update_uris(raw)

        for uri in self.uris:
            if uri.filename == "Release.gpg":
                release_uri = Uri(re.sub(".gpg", "", uri.url))
                release_uri.destfile = re.sub(".gpg", "", uri.destfile)
                release_uri.get(self.paths.lists)
                
                #reminder: get release.gpg and verifyrelease integrity
                #uri.get(self.paths["Dir::State::Lists"])
                #uri.gpg_verify...

        for uri in self.uris:
            if uri.filename == "Packages.bz2":
                updated = True
                unpacked = uri.destfile
                uri.destfile = uri.destfile + ".bz2"
                lists = self.paths.lists
                uri.set_path(lists)
                
                m = re.match("(.*)_(.*)_(.*)_Packages.bz2", uri.destfile)
                if m and isfile(uri.path):
                    release = "%s/%s_%s" % (lists, m.group(1), "Release")
                    md5 = md5sum(uri.path)
                    for line in file(release).readlines():
                        if re.search(md5, line):
                            updated = False
                            break
                if updated:
                    uri.get()
                    system("bzcat %s > %s" % (uri.path,(join(lists,unpacked))))

    def install(self, packages, dir, tree, force):
        raw = self._cmdget("-y install %s" % list2str(packages))
        self._parse_install_uris(raw)
        
        if len(self.uris) == 0:
            print "Package `%s' not found" % packages[0]
            print "Querying index..."
            c = Cache(self.paths, self.options, self.archives)
            c.query(packages[0], info=False, names=True, stats=False)
            abort()

        size = 0
        print "Packages to get:"
        for uri in self.uris:
            print "  " + uri.filename
            size += uri.size
        
        print "Amount of packages: %i" % len(self.uris)
        print "Need to get %s of archives" % pretty_size(size)

        if not force:
            print "Do you want to continue [y/N]?",
            if not raw_input() in ['Y', 'y']:
                abort("aborted by user")
        
        for uri in self.uris:
            uri.get(dir, tree)
            uri.md5_verify()
            uri.archive(self.archives)

class StatePaths(Paths):
    def __init__(self, path):
        Paths.__init__(self, path, ['apt', 'dpkg'])
        
        self.dpkg = Paths(self.dpkg, ['status'])

class State:
    def init_create(self, path):
        paths = StatePaths(path)
        
        mkdir_parents(paths.apt)
        mkdir_parents(paths.dpkg)
        file(paths.dpkg.status, "w").write("")
    
    def __init__(self, path):
        self.paths = StatePaths(path)
        
        if (not isdir(str(self.paths.apt)) or 
            not isdir(str(self.paths.dpkg))):
            
            self.init_create(path)

class CacheOptions:
    def __init__(self, container, cache, state):
        generic = {'Dir':                  container,
                   'Dir::Etc':             container.config,
                   'Dir::Cache::Archives': container.archives,
                   'Dir::State':           state.apt,
                   'Dir::State::status':   state.dpkg.status
                  }
        
        remote =  {'Dir::Cache':           cache.remote,
                   'Dir::State::Lists':    cache.remote.lists,
                   'Dir::Etc::SourceList': container.config.sources_list
                  }

        local =   {'Dir::Cache':           cache.local,
                   'Dir::State::Lists':    cache.local.lists,
                   'Dir::Etc::SourceList': cache.local.sources_list
                  }

        generic_opts = self._generate_opts(generic)
        self.remote = generic_opts + self._generate_opts(remote)
        self.local  = generic_opts + self._generate_opts(local)
   
    def _generate_opts(self, dict):
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
    
    def __init__(self, paths, options, archives):
        self.paths = paths
        self.options = options
        self.archives = archives
        
        # reminder: arch
        self.local_pkgcache = join(self.paths.lists, 
                                   "_dists_local_debs_binary-i386_Packages")

    def _cmdcache(self, opts):
        system("apt-cache %s %s" % (self.options, opts))
    
    def generate(self):
        self._cmdcache("gencaches")

    def refresh(self):
        if re.match("(.*)remote/lists(.*)", self.options):
            get = Get(self.paths, self.options, self.archives)
            get.update()
        else:
            system("apt-ftparchive packages %s > %s" % (self.archives,
                                                        self.local_pkgcache))
        self.generate()

    def query(self, package, info, names, stats):
        if re.match("(.*)local/lists(.*)", self.options):
            if not exists(self.local_pkgcache) or not getsize(self.local_pkgcache) > 0:
                abort("container empty")
                
        if not package and not info and not names:
            # list all packages with short description
            self._cmdcache("search . | sort")
            
        elif not package and not info and names:
            # list all packages (without description)
            self._cmdcache("pkgnames | sort")
            
        elif not package and info and not names:
            # list full package information on all packages
            self._cmdcache("dumpavail")
            
        elif package and not info and not names:
            # list all packages with short desc that match package_glob
            self._cmdcache("search %s | sort" % package)

        elif package and not info and names:
            # list all packages (without description) that match a package_glob
            self._cmdcache("pkgnames %s | sort" % package)
        
        elif package and info and not names:
            # list info on specific package
            self._cmdcache("show %s" % package)
        
        else:
            print "options provided do not match a valid query"
            
        if stats:
            print
            self._cmdcache("stats")

class Apt:
    def init_create(self, path):
        paths = CachePaths(path)
        
        mkdir_parents(join(paths.local.lists, "partial"))
        mkdir_parents(join(paths.remote.lists,"partial"))
    
    def __init__(self, container, create=False):
        home = os.environ.get("CHANKO_HOME",
                              join(os.environ.get("HOME"), ".chanko"))
        path = join(home, "caches", file(container.config.hash).read())

        self.paths = CachePaths(path)
        self.state = State(join(home, "state"))
        self.options = CacheOptions(container, self.paths, self.state.paths)
        
        if (not isdir(str(self.paths.local)) or 
            not isdir(str(self.paths.remote))):
                
            if create:
                self.init_create(path)
            else:
                fatal("no cache found at" + path)
        
        sourceslist = "deb file:/// local debs"
        file(self.paths.local.sources_list, "w").write(sourceslist)
        
        self.remote_cache = Cache(self.paths.remote,
                                  self.options.remote,
                                  container.archives)
                                  
        self.local_cache  = Cache(self.paths.local,
                                  self.options.local,
                                  container.archives)
                                  
        self.get = Get(self.paths.remote,
                       self.options.remote,
                       container.archives)


