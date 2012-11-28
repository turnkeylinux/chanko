# Copyright (c) 2012 Alon Swartz <alon@turnkeylinux.org>
#
# This file is part of Chanko
#
# Chanko is free software; you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.

import os
from utils import makedirs

class Log:
    def __init__(self, path):
        self.path = str(path)
        makedirs(self.path)

    def update(self, pkgnames, metadata=""):
        for pkgname in pkgnames:
            pkgpath = os.path.join(self.path, pkgname)
            if not os.path.exists(pkgpath):
                file(pkgpath, "w").write(metadata)

    def list(self):
        packages = {}
        for pkgname in os.listdir(self.path):
            pkgpath = os.path.join(self.path, pkgname)
            if not os.path.isfile(pkgpath):
                continue

            metadata = file(pkgpath).read().strip()
            if not packages.has_key(metadata):
                packages[metadata] = []

            packages[metadata].append(pkgname)

        return packages

