# Copyright (c) 2012 Alon Swartz <alon@turnkeylinux.org>
#
# This file is part of Chanko
#
# Chanko is free software; you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.

import os
import re
import hashlib

import executil

class Error(Exception):
    pass

class Uri:
    def __init__(self, uri, destpath):
        url, destfile, extra = uri.split(' ', 2)
        self.url = url.strip("'")
        self.destfile = destfile
        self.path = os.path.join(destpath, self.destfile)

    @property
    def filename(self):
        return os.path.basename(self.url)

    @property
    def release(self):
        hostname = self.url.split("/")[2]
        m = re.match("(.*)_dists_(.*)_(.*)", self.destfile)
        if m.group(3) == 'Packages':
            s = m.group(2).split("_")
            s.pop()
            s.pop()
            return hostname + "_" + "_".join(s)
        else:
            return hostname + "_" + m.group(2)

    def download(self):
        print "* get: " + self.destfile
        if self.filename == "Packages.bz2":
            path = self.path + ".bz2"
            executil.system("curl -L -f %s -o %s" % (self.url, path))
            executil.system("bzcat %s > %s" % (path, self.path))

        elif self.filename == "Packages.gz":
            path = self.path + ".gz"
            executil.system("curl -L -f %s -o %s" % (self.url, path))
            executil.system("zcat %s > %s" % (path, self.path))

        else:
            executil.system("curl -L -f %s -o %s" % (self.url, self.path))

class Release:
    def __init__(self, name, chanko):
        self.name = name
        self.chanko = chanko

        self.uri_release = None
        self.uri_release_gpg = None
        self.uri_indexes = []

        self.release_content = None

    def add_uri(self, uri):
        if uri.filename == "Release":
            self.uri_release = uri

        if uri.filename == "Release.gpg":
            self.uri_release_gpg = uri

        if uri.filename == "Packages.bz2":
            self.uri_indexes.append(uri)

    def _index_in_release(self, index_path, release_content):
        if not os.path.exists(index_path):
            return False

        digest = hashlib.md5(file(index_path, 'rb').read()).hexdigest()
        if re.search(digest, release_content):
            return True

        return False

    def refresh(self):
        self.uri_release.download()
        self.uri_release_gpg.download()

        executil.getoutput("gpgv", "--keyring", self.chanko.trustedkeys,
                           self.uri_release_gpg.path, self.uri_release.path)

        release_content = file(self.uri_release.path).read()

        for uri_index in self.uri_indexes:
            # skip download if latest
            if self._index_in_release(uri_index.path, release_content):
                continue

            # attempt download of Packages.bz2, fallback to Packages.gz
            try:
                uri_index.download()
            except executil.ExecError, e:
                if uri_index.filename == "Packages.bz2" and not e.exitcode == 22:
                    raise e

                print "* info: Packages.bz2 not available, falling back to gzip..."
                uri_index.url = uri_index.url.replace("bz2", "gz")
                uri_index.download()

            # verify integrity, delete on failure
            if not self._index_in_release(uri_index.path, release_content):
                os.remove(uri_index.path)
                raise Error("verification failed: ", uri_index.path)

def refresh(chanko, cache):
    releases = {}
    raw = executil.getoutput("apt-get %s --print-uris update" % cache.options)
    for r in raw.split("\n"):
        if "Translation" in r:
            continue

        # hack to fallback to old release files until properly supported
        if "InRelease" in r:
            for f in ("Release", "Release.gpg"):
                uri = Uri(r.replace("InRelease", f), destpath=cache.cache_lists)
                release = releases.get(uri.release, Release(uri.release, chanko))
                release.add_uri(uri)
                releases[uri.release] = release
            continue

        uri = Uri(r, destpath=cache.cache_lists)
        release = releases.get(uri.release, Release(uri.release, chanko))
        release.add_uri(uri)
        releases[uri.release] = release

    for release in releases.values():
        release.refresh()

