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
        url, destfile, bytes, hash = uri.split(' ')
        self.url = url.strip("'")
        self.path = os.path.join(destpath, destfile)
        self.name, self.version = destfile.split("_")[:2]
        self.bytes = int(bytes)
        self.hashtype, self.digest = hash.split(":")
        self.filename = os.path.basename(self.url)

    def download(self):
        print "* get: " + self.filename
        executil.system("ccurl", self.url, self.path)

        # verify integrity, delete on failure
        content = file(self.path, 'rb').read()
        digest = getattr(hashlib, self.hashtype.lower())(content).hexdigest()
        if not digest == self.digest:
            os.remove(self.path)
            raise Error("verification failed: ", self.filename)

def get_uris(chanko, cache, packages, nodeps=False):
    try:
        cmd = "apt-get %s --print-uris -y install" % (cache.options)
        raw = executil.getoutput(cmd, *packages)
    except executil.ExecError, e:
        if re.search("Couldn\'t find package", e[2]):
            print "Couldn't find package '%s'" % e[2].split()[-1]
            return []
        else:
            raise Error("get_uris raised error: ", e)
    
    uris = []
    for r in raw.split("\n"):
        if r.startswith("Need to get 0B"):
            return []

        if not r.startswith("'"):
            continue

        uris.append(Uri(r, chanko.archives))

    if nodeps:
        uris_nodeps = []
        for uri in uris:
            if uri.name in packages:
                uris_nodeps.append(uri)

        uris = uris_nodeps

    return uris

def download_uris(uris):
    for uri in uris:
        uri.download()

    return True

