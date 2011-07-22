import os
import re
from os.path import *

import executil

from common import mkdir, md5sum, sha256sum, parse_inputfile

class Error(Exception):
    pass

class ChecksumError(Exception):
    """Accessible attibutes:
    path           path of file which failed checksum verification
    expected       expected checksum
    calculated     calculated checksum
    """

    def __init__(self, path, expected, calculated):
        Exception.__init__(self, path, expected, calculated)

        self.path = path
        self.expected = expected
        self.calculated = calculated

    def __str__(self):
        str = "checksum verification failed: %s" % self.path
        str += "\nexpected: %s" % self.expected
        str += "\ncalculated: %s" % self.calculated

        return str

class Uri:
    def __init__(self, url):
        self.url = url
        self.filename = basename(url)
        self.destfile = None
        self.path = None
        self.release = None
        self.checksum = None
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

    def checksum_verify(self):
        if not self.path:
            raise Error("no path set for: " + self.filename)

        if not self.checksum:
            raise Error("no checksum set for: " + self.path)

        if not len(self.checksum) in (32, 64):
            raise Error('unknown checksum size: %s' % self.path)

        if len(self.checksum) == 32:
            if not self.checksum == md5sum(self.path):
                raise ChecksumError(self.path, self.checksum, md5sum(self.path))
        else:
            if not self.checksum == sha256sum(self.path):
                raise ChecksumError(self.path, self.checksum, sha256sum(self.path))

    def link(self, link_path):
        dest = join(link_path, self.destfile)
        if not islink(dest):
            os.symlink(self.path, dest)

class Release:
    def __init__(self, name, keyring, gcache, lists):
        self.name = name
        self.keyring = keyring
        self.gcache = gcache
        self.lists = lists

        self.gpg = None
        self.release = None
        self.repositories = []

    def update(self):
        self.release.get(self.gcache)
        self.release.link(self.lists)

        self.gpg.get(self.gcache)
        self.gpg.link(self.lists)

        # will raise an error if verification fails
        executil.getoutput("gpgv --keyring", self.keyring, self.gpg.path, self.release.path)

        for repository in self.repositories:
            self._update_repository(repository)

    def _update_repository(self, uri):
        uri.set_path(self.gcache)
        uri.link(self.lists)

        m = re.match("(.*)_(.*)_(.*)_Packages", uri.destfile)
        if m:
            release_path = join(self.lists, m.group(1)) + "_Release"
            release_content = file(release_path).read()

        #skip download if local packages file is latest
        if exists(uri.path) and re.search(md5sum(uri.path), release_content):
            return

        unpack_path = join(self.gcache, uri.destfile)
        uri.set_destfile(uri.destfile + ".bz2")
        uri.set_path(self.gcache)
        uri.get()

        if not re.search(md5sum(uri.path), release_content):
            raise ChecksumError(uri.path,
                                "releases file: %s" % release_path,
                                md5sum(uri.path))

        executil.system("bzcat %s > %s" % (uri.path, unpack_path))


class Get:
    def __init__(self, cache_paths, chanko_paths, options, gcache):
        self.cache_paths = cache_paths
        self.chanko_paths = chanko_paths
        self.options = options
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
                    uri.release = uri.destfile.split("_")[3]

                    uris.append(uri)
        return uris

    @staticmethod
    def _parse_install_uris(raw):
        uris = []
        for line in raw.split("\n"):
            if re.match("Need to get 0B(.*)", line):
                return []

            m = re.match("\'(.*)\' (.*) (.*) (.*)", line)
            if m:
                uri = Uri(m.group(1))
                uri.size = int(m.group(3))
                uri.checksum = re.sub('SHA256:', '', m.group(4))

                uris.append(uri)
        return uris

    def update(self):
        keyring = self.chanko_paths.config.trustedkeys_gpg
        if not exists(keyring):
            raise Error("trustedkeys keyring not found: %s" % keyring)

        raw = self._cmdget("update")
        uris = self._parse_update_uris(raw)

        releases = []
        for uri in uris:
            if uri.release not in releases:
                releases.append(uri.release)
                release = Release(uri.release,
                                  keyring,
                                  self.gcache,
                                  self.cache_paths.lists)
   
            if uri.filename == "Packages.bz2":
                release.repositories.append(uri)

            if uri.filename == "Release":
                release.release = uri

            if uri.filename == "Release.gpg":
                release.gpg = uri
                release.update()

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

    def _remove_blacklisted(self, uris):
        blacklist_path = self.chanko_paths.config.blacklist
        if not exists(blacklist_path) or len(uris) == 0:
            return uris

        blacklist = parse_inputfile(blacklist_path)
        if len(blacklist) == 0:
            return uris

        cleaned_uris = []
        for uri in uris:
            name, version = uri.filename.split("_")[:2]
            if name in blacklist:
                print "Blacklisted package: %s" % uri.filename
            else:
                cleaned_uris.append(uri)

        return cleaned_uris

    def get_install_uris(self, packages):
        try:
            raw_uris = self._cmdget("-y install %s" % " ".join(packages))
        except executil.ExecError, e:
            if re.search("Couldn\'t find package", e[2]):
                print "Couldn't find package '%s'" % e[2].split()[-1]
            else:
                raise Error("cmdget returned error: ", e)

            return False

        uris = self._parse_install_uris(raw_uris)
        uris = self._remove_blacklisted(uris)
        return uris

    def install(self, packages, force):
        uris = self.get_install_uris(packages)
        if len(uris) == 0:
            print "Archive(s) already in chanko"
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
                print "aborted by user"
                return False

        for uri in uris:
            uri.get(self.chanko_paths.archives)
            uri.checksum_verify()

        return True


