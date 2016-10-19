#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\utils\__init__.py
from __future__ import absolute_import
from raven._compat import iteritems, string_types
import logging
import threading
from functools import update_wrapper
try:
    import pkg_resources
except ImportError:
    pkg_resources = None

import sys
logger = logging.getLogger('raven.errors')

def merge_dicts(*dicts):
    out = {}
    for d in dicts:
        if not d:
            continue
        for k, v in iteritems(d):
            out[k] = v

    return out


def varmap(func, var, context = None, name = None):
    if context is None:
        context = {}
    objid = id(var)
    if objid in context:
        return func(name, '<...>')
    context[objid] = 1
    if isinstance(var, dict):
        ret = dict(((k, varmap(func, v, context, k)) for k, v in iteritems(var)))
    elif isinstance(var, (list, tuple)):
        ret = [ varmap(func, f, context, name) for f in var ]
    else:
        ret = func(name, var)
    del context[objid]
    return ret


_VERSION_CACHE = {}

def get_version_from_app(module_name, app):
    version = None
    if pkg_resources is not None:
        try:
            return pkg_resources.get_distribution(module_name).version
        except Exception:
            pass

    if hasattr(app, 'get_version'):
        version = app.get_version
    elif hasattr(app, '__version__'):
        version = app.__version__
    elif hasattr(app, 'VERSION'):
        version = app.VERSION
    elif hasattr(app, 'version'):
        version = app.version
    if callable(version):
        version = version()
    if not isinstance(version, (string_types, list, tuple)):
        version = None
    if version is None:
        return
    if isinstance(version, (list, tuple)):
        version = '.'.join(map(str, version))
    return str(version)


def get_versions(module_list = None):
    if not module_list:
        return {}
    ext_module_list = set()
    for m in module_list:
        parts = m.split('.')
        ext_module_list.update(('.'.join(parts[:idx]) for idx in range(1, len(parts) + 1)))

    versions = {}
    for module_name in ext_module_list:
        if module_name not in _VERSION_CACHE:
            try:
                __import__(module_name)
            except ImportError:
                continue

            try:
                app = sys.modules[module_name]
            except KeyError:
                continue

            try:
                version = get_version_from_app(module_name, app)
            except Exception as e:
                logger.exception(e)
                version = None

            _VERSION_CACHE[module_name] = version
        else:
            version = _VERSION_CACHE[module_name]
        if version is None:
            continue
        versions[module_name] = version

    return versions


def get_auth_header(protocol, timestamp, client, api_key, api_secret = None, **kwargs):
    header = [('sentry_timestamp', timestamp),
     ('sentry_client', client),
     ('sentry_version', protocol),
     ('sentry_key', api_key)]
    if api_secret:
        header.append(('sentry_secret', api_secret))
    return 'Sentry %s' % ', '.join(('%s=%s' % (k, v) for k, v in header))


class memoize(object):

    def __init__(self, func):
        self.__name__ = func.__name__
        self.__module__ = func.__module__
        self.__doc__ = func.__doc__
        self.func = func

    def __get__(self, obj, type = None):
        if obj is None:
            return self
        d, n = vars(obj), self.__name__
        if n not in d:
            d[n] = self.func(obj)
        return d[n]


def once(func):
    lock = threading.Lock()

    def new_func(*args, **kwargs):
        if new_func.called:
            return
        with lock:
            if new_func.called:
                return
            rv = func(*args, **kwargs)
            new_func.called = True
            return rv

    new_func = update_wrapper(new_func, func)
    new_func.called = False
    return new_func
