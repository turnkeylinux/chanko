# Copyright (c) 2010 Alon Swartz <alon@turnkeylinux.org> - all rights reserved

import os
import re
import errno
import commands
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
    
    @staticmethod
    def _sumocmd(opts):
        # CHANKO_BASE _should be_ equivalent to SUMO_BASE
        # currently we have to chdir into SUMO_BASE, setting env doesn't work
        cwd = os.getcwd()
        os.chdir(os.getenv('CHANKO_BASE', cwd))
        system("sumo-" + opts)
        os.chdir(cwd)

    def set_destfile(self, destfile):
        self.destfile = destfile
        
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
        makedirs(dirname(self.path))
        if re.match("(.*).deb", self.path):
            self._sumocmd("get %s %s" % (self.url, self.path))
        else:
            system("curl -L -f %s -o %s" % (self.url, self.path))

    def md5_verify(self):
        if not self.path:
            raise Error("no path set for: " + self.filename)
        
        if not self.md5:
            raise Error("no md5 set for: " + self.path)

        if not self.md5 == md5sum(self.path):
            raise Error("md5sum verification failed: %s" % self.path)

    def archive(self, archive_path):
        dest = join(archive_path, self.filename)
        self._sumocmd("cp -l %s %s" % (self.path, dest))
        
    def link(self, link_path):
        dest = join(link_path, self.destfile)
        if not islink(dest):
            os.symlink(self.path, dest)

class Get:
    def __init__(self, paths, options, archives, gcache):
        self.paths = paths
        self.options = options
        self.archives = archives
        self.gcache = gcache

    def _cmdget(self, opts):
        cmd = "apt-get %s --print-uris %s" % (self.options, opts)
        return commands.getstatusoutput(cmd)
    
    @staticmethod
    def _parse_update_uris(raw):
        uris = []
        for uri in raw.split("\n"):
            m = re.match("\'(.*)\' (.*) 0", uri)
            if m:
                if not re.match("(.*)Translation(.*)", m.group(1)):
                    uri = Uri(m.group(1))
                    uri.destfile = m.group(2)

                    uris.append(uri)
        return uris

    @staticmethod
    def _parse_install_uris(raw):
        uris = []
        for line in raw.split("\n"):
            if re.match("Need to get 0B(.*)", line):
                raise Error("Newest version already in container")
            
            m = re.match("\'(.*)\' (.*) (.*) (.*)", line)
            if m:
                uri = Uri(m.group(1))
                uri.size = int(m.group(3))
                uri.md5 = m.group(4)
                
                uris.append(uri)
        return uris
    
    def update(self):
        err, raw = self._cmdget("update")
        uris = self._parse_update_uris(raw)

        for uri in uris:
            if uri.filename == "Release.gpg":
                release_uri = Uri(re.sub(".gpg", "", uri.url))
                release_uri.set_destfile(re.sub(".gpg", "", uri.destfile))
                release_uri.get(self.gcache)
                release_uri.link(self.paths.lists)
                
                #reminder: get release.gpg and verify release integrity
                #uri.get...
                #uri.gpg_verify...

        for uri in uris:
            if uri.filename == "Packages.bz2":
                updated = True

                uri.set_path(self.gcache)
                uri.link(self.paths.lists)
                
                unpacked = uri.destfile
                uri.set_destfile(uri.destfile + ".bz2")
                uri.set_path(self.gcache)

                m = re.match("(.*)_(.*)_(.*)_Packages.bz2", uri.destfile)
                if m and isfile(uri.path):
                    release = join(self.paths.lists, m.group(1)) + "_Release"
                    md5 = md5sum(uri.path)
                    for line in file(release).readlines():
                        if re.search(md5, line):
                            updated = False
                            break

                if updated:
                    uri.get()
                    system("bzcat %s > %s" % (uri.path,
                                              join(self.gcache, unpacked)))

    def install(self, packages, dir, tree, force):
        err, raw = self._cmdget("-y install %s" % " ".join(packages))
        uris = self._parse_install_uris(raw)
        
        if len(uris) == 0:
            if re.search("Couldn\'t find package", raw):
                print "Couldn't find package `%s'" % packages[0]
                print "Querying index for similar package..."
                c = Cache(self.paths, self.options, self.archives, self.gcache)
                c.query(packages[0], info=False, names=True, stats=False)
            else:
                raise Error ("cmdget returned error: ", err, raw)

            return False

        size = 0
        print "Packages to get:"
        for uri in uris:
            print "  " + uri.filename
            size += uri.size
        
        print "Amount of packages: %i" % len(uris)
        print "Need to get %s of archives" % pretty_size(size)

        if not force:
            print "Do you want to continue [y/N]?",
            if not raw_input() in ['Y', 'y']:
                raise Error("aborted by user")
        
        for uri in uris:
            uri.get(dir, tree)
            uri.md5_verify()
            uri.archive(self.archives)
        
        return True

class StatePaths(Paths):
    def __init__(self, path):
        Paths.__init__(self, path, ['apt', 'dpkg'])
        
        self.dpkg = Paths(self.dpkg, ['status'])

class State:
    def __init__(self, path):
        self.paths = StatePaths(path)
        
        if (not isdir(str(self.paths.apt)) or 
            not isdir(str(self.paths.dpkg))):
            
            makedirs(self.paths.apt)
            makedirs(self.paths.dpkg)
            file(self.paths.dpkg.status, "w").write("")

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
    
    def __init__(self, paths, options, archives, gcache):
        self.paths = paths
        self.options = options
        self.archives = archives
        self.gcache = gcache
        
        # reminder: arch
        self.local_pkgcache = join(self.paths.lists, 
                                   "_dists_local_debs_binary-i386_Packages")

    def _cmdcache(self, opts):
        system("apt-cache %s %s" % (self.options, opts))
    
    def refresh(self):
        if re.match("(.*)remote/lists(.*)", self.options):
            get = Get(self.paths, self.options, self.archives, self.gcache)
            get.update()
        else:
            system("apt-ftparchive packages %s > %s" % (self.archives,
                                                        self.local_pkgcache))
        self._cmdcache("gencaches")

    def query(self, package, info, names, stats):
        if re.match("(.*)local/lists(.*)", self.options):
            
            if (not exists(self.local_pkgcache) or
                not getsize(self.local_pkgcache) > 0):
                   
                raise Error("container empty")
                
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
    def __init__(self, container, create=False):
        home = os.environ.get("CHANKO_HOME",
                              join(os.environ.get("HOME"), ".chanko"))
        path = join(home, "caches", file(container.config.hash).read())
        gcache = join(home, "caches", "global")

        paths = CachePaths(path)
        state = State(join(home, "state"))
        options = CacheOptions(container, paths, state.paths)
        
        if (not isdir(str(paths.local)) or 
            not isdir(str(paths.remote)) or
            not isdir(gcache)):
            
            makedirs(join(paths.local.lists, "partial"))
            makedirs(join(paths.remote.lists,"partial"))
            makedirs(gcache)
        
        sourceslist = "deb file:/// local debs"
        file(paths.local.sources_list, "w").write(sourceslist)
        
        self.remote_cache = Cache(paths.remote,
                                  options.remote,
                                  container.archives,
                                  gcache)
                                  
        self.local_cache  = Cache(paths.local,
                                  options.local,
                                  container.archives,
                                  gcache)
                                  
        self.get = Get(paths.remote,
                       options.remote,
                       container.archives,
                       gcache)


