# Copyright (c) 2010 Alon Swartz <alon@turnkeylinux.org> - all rights reserved

import os
import re
import errno
import shutil
from os.path import *

from utils import *

class Get:
    def __init__(self, paths, options):
        self.paths = paths
        self.options = options

    def _parse_update_uris(self, raw):
        uris = []
        for uri in raw.split("\n"):
            m = re.match("\'(.*)\' (.*) 0", uri)
            if m:
                if not re.match("(.*)Translation(.*)", m.group(1)):
                    uri = {'url':  m.group(1),
                           'file': m.group(2)
                          }
                    uris.append(uri)
        return uris

    def _parse_install_uris(self, raw):
        uris = []
        for line in raw.split("\n"):
            m = re.match("\'(.*)\' (.*) (.*) (.*)", line)
            if m:
                uri = {'url':  m.group(1),
                       'file': m.group(2),
                       'size': m.group(3),
                       'md5':  m.group(4)
                      }
                uris.append(uri)
        return uris

    def _md5sum(self, path):
        return getoutput("md5sum %s | awk '{print $1}'" % path)

    def _download(self, url, dir, filename=None):
        # if container is in sumo arena, use sumo-get, otherwise use curl
        # curl
        if filename:
            dst = dir + "/" + filename
        else:
            dst = dir + "/" + basename(url)
        
        print "* getting: %s" % basename(dst)
        system("curl -L -f %s -o %s" % (url, dst))
        return dst

    def _treepath(self, file):
        name = file.split("_")[0]
        m = re.match("^lib(.*)", name)
        if m:
            prefix = "lib" + m.group(1)[0]
        else:
            prefix = name[0]
        return prefix + "/" + name
        
    def _store(self, path, dest):
        try:
            os.link(path, dest)
        except OSError, e:
            if e[0] != errno.EXDEV:
                raise e
            warn("copying file into cache instead of hard-linking")
            shutil.copyfile(path, dest)

    def update(self):
        raw = getoutput("apt-get %s --print-uris update" % self.options)
        uris = self._parse_update_uris(raw)

        for uri in uris:
            if basename(uri["url"]) == "Release.gpg":
                #reminder: get release.gpg and check integrity
                self._download(re.sub(".gpg", "", uri["url"]),
                               self.paths["Dir::State::Lists"],
                               re.sub(".gpg", "", uri["file"]))

        for uri in uris:
            if basename(uri["url"]) == "Packages.bz2":
                path = self.paths["Dir::State::Lists"] + "/" + uri["file"]
                if isfile(path):
                    m = re.match("(.*)_(.*)_(.*)_Packages", uri["file"])
                    if m:
                        rel = "%s/%s%s" % (self.paths["Dir::State::Lists"], m.group(1), "_Release")
                        cmd = "grep -q %s %s" % (self._md5sum(path), rel)
                        if not getstatus(cmd):
                            continue

                self._download(uri["url"],
                               self.paths["Dir::State::Lists"],
                               (uri["file"] + ".bz2"))
                system("bzcat %s > %s" % ((path + ".bz2"), path))

                
    def install(self, packages, dir, tree, force):
        packages_str = ""
        for p in packages:
            packages_str = packages_str + p + " "

        raw = getoutput("apt-get %s --print-uris -y install %s" % (self.options,
                                                                   packages_str))
        uris = self._parse_install_uris(raw)
        if len(uris) == 0:
            print "Package `%s' not found, below are the query results:" % packages[0]
            c = Cache(self.paths, self.options)
            c.query(packages[0], info=False, names=True, stats=False)
            abort()

        size = 0
        print "Packages to get:"
        for uri in uris:
            print "  " + basename(uri["url"])
            size += int(uri['size'])
        
        print "Amount of packages: %s" % len(uris)
        if size < 1000000:
            print "Need to get ~%iKB of archives" % (size/1024)
        else:
            print "Need to get ~%iMB of archives" % (size/(1024*1024))

        if not force:
            print "Do you want to continue [y/N]?",
            if not raw_input() in ['Y', 'y']:
                abort("aborted by user")
        
        for uri in uris:
            if tree:
                getdir = dir + "/" + self._treepath(basename(uri["url"]))
                mkdir_parents(getdir)
            else:
                getdir = dir
            path = self._download(uri["url"], getdir)
            if not self._md5sum(path) == uri["md5"]:
                raise Error("md5sum mismatch: %s" % path)
            archive = self.paths["Dir::Cache::Archives"] + "/" + basename(path)
            self._store(path, archive)
    
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

        
