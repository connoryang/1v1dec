#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\utils\compat.py
from __future__ import absolute_import
try:
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import HTTPError

try:
    import httplib
except ImportError:
    from http import client as httplib

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

Request = urllib2.Request
urlopen = urllib2.urlopen
try:
    from urllib import quote as urllib_quote
except ImportError:
    from urllib.parse import quote as urllib_quote

try:
    from queue import Queue
except ImportError:
    from Queue import Queue

try:
    import urlparse as _urlparse
except ImportError:
    from urllib import parse as _urlparse

urlparse = _urlparse

def check_threads():
    try:
        from uwsgi import opt
    except ImportError:
        return

    if str(opt.get('enable-threads', '0')).lower() in ('false', 'off', 'no', '0'):
        from warnings import warn
        warn(Warning('We detected the use of uwsgi with disabled threads.  This will cause issues with the transport you are trying to use.  Please enable threading for uwsgi.  (Enable the "enable-threads" flag).'))
