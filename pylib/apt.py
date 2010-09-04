# Copyright (c) 2010 Alon Swartz <alon@turnkeylinux.org> - all rights reserved

import os
import re
import errno
import shutil
import string
from os.path import *

from utils import *

class Uri:
    def __init__(self, url):
        self.url = url
        self.filename = basename(url)
        self.destfile = None
        self.tree = treepath(self.filename)
        self.path = None
        self.md5 = None
        self.size = 0

    def set_path(self, dir, tree=False):
        if not dir:
            raise Error("dir not passed for: " + self.url)
        
        if self.destfile:
            filename = self.destfile
        else:
            filename = self.filename
        
        if tree:
            self.path = string.join([dir, self.tree, filename], "/")
        else:
            self.path = string.join([dir, filename], "/")

    def get(self, dir=None, tree=False):
        #reminder: update for sumo
        if not self.path:
            self.set_path(dir, tree)
            
        print "* getting: " + basename(self.path)
        system("curl -L -f %s -o %s" % (self.url, self.path))

    def md5_verify(self):
        if not self.path:
            fatal("no path set for: " + self.filename)
        
        if not self.md5:
            fatal("no md5 set for: " + self.path)

        if not self.md5 == md5sum(self.path):
            fatal("md5sum verification failed: %s" % self.path)
        
    def archive(self, archive_path):
        dest = string.join([archive_path, self.filename], "/")
        try:
            os.link(self.path, dest)
        except OSError, e:
            if e[0] != errno.EXDEV:
                raise e
            warn("copying file into archive instead of hard-linking")
            shutil.copyfile(path, dest)

class Get:
    def __init__(self, paths, options):
        self.paths = paths
        self.options = options

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
                release_uri.get(self.paths["Dir::State::Lists"])
                
                #reminder: get release.gpg and verifyrelease integrity
                #uri.get(self.paths["Dir::State::Lists"])
                #uri.gpg_verify...

        for uri in self.uris:
            if uri.filename == "Packages.bz2":
                updated = True
                unpacked = uri.destfile
                uri.destfile = uri.destfile + ".bz2"
                lists = self.paths["Dir::State::Lists"]
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
                    system("bzcat %s > %s" % (uri.path, (lists+"/"+unpacked)))

    def install(self, packages, dir, tree, force):
        raw = self._cmdget("-y install %s" % list2str(packages))
        self._parse_install_uris(raw)
        
        if len(self.uris) == 0:
            print "Package `%s' not found" % packages[0]
            print "Querying index..."
            c = Cache(self.paths, self.options)
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
            uri.archive(self.paths["Dir::Cache::Archives"])

    
class Cache:
    """ class for controlling chanko container cache """
    
    def __init__(self, paths, options):
        self.paths = paths
        self.options = options

    def generate(self):
        system("apt-cache %s gencaches" % self.options)
    
    def refresh(self):
        if re.match("(.*)remote", self.paths["Dir::Cache"]):
            get = Get(self.paths, self.options)
            get.update()            
        else:
            # reminder: arch
            pkg_cache = self.paths["Dir::State::Lists"] + "/_dists_local_debs_binary-i386_Packages"
            system("apt-ftparchive packages %s > %s" % (
                    self.paths["Dir::Cache::Archives"], pkg_cache))

        self.generate()

    def query(self, package, info, names, stats):
        if not package and not info and not names:
            # list all packages with short description
            # chanko-query (-r|-l)
            system("apt-cache %s search . | sort" % self.options)
            
        elif not package and not info and names:
            # list all packages (without description)
            # chanko-query (-r|-l) --names
            system("apt-cache %s pkgnames | sort" % self.options)
            
        elif not package and info and not names:
            # list full package information on all packages
            # chanko-query (-r|-l) --info
            system("apt-cache %s dumpavail" % self.options)
            
        elif package and not info and not names:
            # list all packages with short desc that match package_glob
            # chanko-query (-r|-l) package_glob
            system("apt-cache %s search %s | sort" % (self.options, package))

        elif package and not info and names:
            # list all packages (without description) that match a package_glob
            # chanko-query (-r|-l) --names package_glob
            system("apt-cache %s pkgnames %s | sort" % (self.options, package))
        
        elif package and info and not names:
            # list info on specific package
            # chanko-query (-r|-l) --info package
            system("apt-cache %s show %s" % (self.options, package))
        
        else:
            print "options provided do not match a valid query"
            
        if stats:
            print
            system("apt-cache %s stats" % self.options)

