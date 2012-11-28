#!/usr/bin/python
# Copyright (c) 2012 Alon Swartz <alon@turnkeylinux.org>
#
# This file is part of Chanko
#
# Chanko is free software; you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.

from os.path import *
import pyproject
 
class CliWrapper(pyproject.CliWrapper):
    DESCRIPTION = __doc__
    INSTALL_PATH = dirname(__file__)
    COMMANDS_USAGE_ORDER = ['get', 'upgrade', 'purge', 'refresh', 'query']

if __name__=='__main__':
    CliWrapper.main()
