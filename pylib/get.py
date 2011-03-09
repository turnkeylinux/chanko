import os
import re
from os.path import *

import executil

from common import mkdir, md5sum

class Error(Exception):
    pass

class Uri:
    def __init__(self, url):
        self.url = url
        self.filename = basename(url)
        self.destfile = None
        self.path = None
        self.md5sum = None
        self.size = 0

    @staticmethod
    def _sumocmd(opts):
        # CHANKO_BASE _should be_ equivalent to SUMO_BASE
        # currently we have to chdir into SUMO_BASE, setting env doesn't work
        cwd = os.getcwd()
        os.chdir(os.getenv('CHANKO_BASE', cwd))
        executil.system("sumo-" + opts)
        os.chdir(cwd)

    def set_destfile(self, destfile):
        self.destfile = destfile

    def set_path(self, dir):
        if not dir:
            raise Error("dir not passed for: " + self.url)

        if self.destfile:
            filename = self.destfile
        else:
            filename = self.filename

        self.path = join(dir, filename)

    def get(self, dir=None):
        if not self.path:
            self.set_path(dir)

        print "* get: " + basename(self.path)
        mkdir(dirname(self.path))
        if self.path.endswith('.deb'):
            self._sumocmd("get %s %s" % (self.url, self.path))
        else:
            executil.system("curl -L -f %s -o %s" % (self.url, self.path))

    def md5_verify(self):
        if not self.path:
            raise Error("no path set for: " + self.filename)

        if not self.md5sum:
            raise Error("no md5sum set for: " + self.path)

        if not self.md5sum == md5sum(self.path):
            raise Error("md5sum verification failed: %s" % self.path)

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
        return executil.getoutput(cmd)

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
                raise Error("Newest version already in chanko")

            m = re.match("\'(.*)\' (.*) (.*) (.*)", line)
            if m:
                uri = Uri(m.group(1))
                uri.size = int(m.group(3))
                uri.md5sum = m.group(4)

                uris.append(uri)
        return uris

    def update(self):
        raw = self._cmdget("update")
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
                    for line in file(release).readlines():
                        if re.search(md5sum(uri.path), line):
                            updated = False
                            break

                if updated:
                    uri.get()
                    executil.system("bzcat %s > %s" % 
                                    (uri.path, join(self.gcache, unpacked)))

    @staticmethod
    def _fmt_bytes(bytes):
        G = (1024 * 1024 * 1024)
        M = (1024 * 1024)
        K = (1024)
        if bytes > G:
            return str(bytes/G) + "G"
        elif bytes > M:
            return str(bytes/M) + "M"
        else:
            return str(bytes/K) + "K"

    def install(self, packages, force):
        try:
            raw = self._cmdget("-y install %s" % " ".join(packages))
            uris = self._parse_install_uris(raw)
        except executil.ExecError, e:
            if re.search("Couldn\'t find package", e[2]):
                print "Couldn't find package `%s'" % packages[0]
                print "Querying index for similar package..."
                c = Cache(self.paths, self.options, self.archives, self.gcache)
                c.query(packages[0], info=False, names=True, stats=False)
            else:
                raise Error("cmdget returned error: ", e)

            return False

        size = 0
        print "Packages to get:"
        for uri in uris:
            print "  " + uri.filename
            size += uri.size

        print "Amount of packages: %i" % len(uris)
        print "Need to get %s of archives" % self._fmt_bytes(size)

        if not force:
            print "Do you want to continue [y/N]?",
            if not raw_input() in ['Y', 'y']:
                raise Error("aborted by user")

        for uri in uris:
            uri.get(self.archives)
            uri.md5_verify()

        return True


