#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\__init__.py
from __future__ import absolute_import
import os
import os.path
__all__ = ('VERSION', 'Client', 'get_version')
VERSION = '5.25.0'

def _get_git_revision(path):
    revision_file = os.path.join(path, 'refs', 'heads', 'master')
    if not os.path.exists(revision_file):
        return
    fh = open(revision_file, 'r')
    try:
        return fh.read().strip()[:7]
    finally:
        fh.close()


def get_revision():
    package_dir = os.path.dirname(__file__)
    checkout_dir = os.path.normpath(os.path.join(package_dir, os.pardir, os.pardir))
    path = os.path.join(checkout_dir, '.git')
    if os.path.exists(path):
        return _get_git_revision(path)


def get_version():
    base = VERSION
    if __build__:
        base = '%s (%s)' % (base, __build__)
    return base


__build__ = get_revision()
__docformat__ = 'restructuredtext en'
from raven.base import *
from raven.conf import *
from raven.versioning import *
