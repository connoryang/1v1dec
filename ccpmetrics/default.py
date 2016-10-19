#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\ccpmetrics\default.py
import os
from .client import Client

def default_client():
    if not hasattr(default_client, '_client'):
        default_client._client = Client(host=os.environ.get('AGGREGATED_CLIENT_HOST', 'dev-metrics.tech.ccp.is'), env_tags=os.environ.get('AGGREGATED_CLIENT_TAGS', {}))
    return default_client._client


def gauge(*args, **kwargs):
    return default_client().gauge(*args, **kwargs)


def increment(*args, **kwargs):
    return default_client().increment(*args, **kwargs)


def decrement(*args, **kwargs):
    return default_client().decrement(*args, **kwargs)


def histogram(*args, **kwargs):
    return default_client().histogram(*args, **kwargs)


def set(*args, **kwargs):
    return default_client().set(*args, **kwargs)


def event(*args, **kwargs):
    return default_client().event(*args, **kwargs)
