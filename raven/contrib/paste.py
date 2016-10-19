#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\contrib\paste.py
from __future__ import absolute_import
from raven.middleware import Sentry
from raven.base import Client

def sentry_filter_factory(app, global_conf, **kwargs):
    client = Client(**kwargs)
    return Sentry(app, client)
