#!/usr/bin/python
# Copyright (c) 2010 TurnKey Linux - all rights reserved
from os.path import *
import pyproject
 
class CliWrapper(pyproject.CliWrapper):
    DESCRIPTION = __doc__
    INSTALL_PATH = dirname(__file__)
    COMMANDS_USAGE_ORDER = ['get', 'upgrade', 'purge', 'refresh', 'query']

if __name__=='__main__':
    CliWrapper.main()
