# -*- coding: utf-8 -*-

"""
Python IPC Wrapper and Implementation
~~~~~~~~~~~~~~~~~~~
A basic IPC implementation for Python 3
:copyright: (c) 2020-2020 dovedevic
:license: GPL, see LICENSE for more details.
"""

__title__ = 'ipyc'
__author__ = 'dovedevic'
__license__ = 'GPL'
__copyright__ = 'Copyright 2020-2020 dovedevic'
__version__ = '1.0.0r'

__path__ = __import__('pkgutil').extend_path(__path__, __name__)

from collections import namedtuple
import logging

from .blocking import IPyCHost, IPyCClient
from . import serialization as IPyCSerialization

VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')
version_info = VersionInfo(major=1, minor=0, micro=0, releaselevel='release', serial=0)

logging.getLogger(__name__).addHandler(logging.NullHandler())
