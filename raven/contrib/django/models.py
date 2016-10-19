#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\contrib\django\models.py
from __future__ import absolute_import, unicode_literals
import logging
import sys
import warnings
from django.conf import settings
from raven._compat import PY2, binary_type, text_type, string_types
from raven.utils.conf import convert_options
from raven.utils.imports import import_string
logger = logging.getLogger(u'sentry.errors.client')

def get_installed_apps():
    return set(settings.INSTALLED_APPS)


_client = (None, None)

class ProxyClient(object):
    __members__ = property(lambda x: x.__dir__())
    __class__ = property(lambda x: get_client().__class__)
    __dict__ = property(lambda o: get_client().__dict__)
    __repr__ = lambda x: repr(get_client())
    __getattr__ = lambda x, o: getattr(get_client(), o)
    __setattr__ = lambda x, o, v: setattr(get_client(), o, v)
    __delattr__ = lambda x, o: delattr(get_client(), o)
    __lt__ = lambda x, o: get_client() < o
    __le__ = lambda x, o: get_client() <= o
    __eq__ = lambda x, o: get_client() == o
    __ne__ = lambda x, o: get_client() != o
    __gt__ = lambda x, o: get_client() > o
    __ge__ = lambda x, o: get_client() >= o
    if PY2:
        __cmp__ = lambda x, o: cmp(get_client(), o)
    __hash__ = lambda x: hash(get_client())
    __nonzero__ = lambda x: bool(get_client())
    __len__ = lambda x: len(get_client())
    __getitem__ = lambda x, i: get_client()[i]
    __iter__ = lambda x: iter(get_client())
    __contains__ = lambda x, i: i in get_client()
    __getslice__ = lambda x, i, j: get_client()[i:j]
    __add__ = lambda x, o: get_client() + o
    __sub__ = lambda x, o: get_client() - o
    __mul__ = lambda x, o: get_client() * o
    __floordiv__ = lambda x, o: get_client() // o
    __mod__ = lambda x, o: get_client() % o
    __divmod__ = lambda x, o: get_client().__divmod__(o)
    __pow__ = lambda x, o: get_client() ** o
    __lshift__ = lambda x, o: get_client() << o
    __rshift__ = lambda x, o: get_client() >> o
    __and__ = lambda x, o: get_client() & o
    __xor__ = lambda x, o: get_client() ^ o
    __or__ = lambda x, o: get_client() | o
    __div__ = lambda x, o: get_client().__div__(o)
    __truediv__ = lambda x, o: get_client().__truediv__(o)
    __neg__ = lambda x: -get_client()
    __pos__ = lambda x: +get_client()
    __abs__ = lambda x: abs(get_client())
    __invert__ = lambda x: ~get_client()
    __complex__ = lambda x: complex(get_client())
    __int__ = lambda x: int(get_client())
    if PY2:
        __long__ = lambda x: long(get_client())
    __float__ = lambda x: float(get_client())
    __str__ = lambda x: binary_type(get_client())
    __unicode__ = lambda x: text_type(get_client())
    __oct__ = lambda x: oct(get_client())
    __hex__ = lambda x: hex(get_client())
    __index__ = lambda x: get_client().__index__()
    __coerce__ = lambda x, o: x.__coerce__(x, o)
    __enter__ = lambda x: x.__enter__()
    __exit__ = lambda x, *a, **kw: x.__exit__(*a, **kw)


client = ProxyClient()

def get_option(x, d = None):
    options = getattr(settings, u'RAVEN_CONFIG', {})
    return getattr(settings, u'SENTRY_%s' % x, options.get(x, d))


def get_client(client = None, reset = False):
    global _client
    tmp_client = client is not None
    if not tmp_client:
        client = getattr(settings, u'SENTRY_CLIENT', u'raven.contrib.django.DjangoClient')
    if _client[0] != client or reset:
        options = convert_options(settings, defaults={u'include_paths': get_installed_apps()})
        try:
            Client = import_string(client)
        except ImportError:
            logger.exception(u'Failed to import client: %s', client)
            if not _client[1]:
                client = u'raven.contrib.django.DjangoClient'
                _client = (client, get_client(client))
        else:
            instance = Client(**options)
            if not tmp_client:
                _client = (client, instance)
            return instance

    return _client[1]


def sentry_exception_handler(request = None, **kwargs):
    try:
        client.captureException(exc_info=sys.exc_info(), request=request)
    except Exception as exc:
        try:
            logger.exception(u'Unable to process log entry: %s' % (exc,))
        except Exception as exc:
            warnings.warn(u'Unable to process log entry: %s' % (exc,))


def register_handlers():
    from django.core.signals import got_request_exception, request_started

    def before_request(*args, **kwargs):
        client.context.activate()

    request_started.connect(before_request, weak=False)
    if u'sentry' in settings.INSTALLED_APPS:
        from django.db import transaction
        if hasattr(transaction, u'atomic'):
            commit_on_success = transaction.atomic
        else:
            commit_on_success = transaction.commit_on_success

        @commit_on_success
        def wrap_sentry(request, **kwargs):
            if transaction.is_dirty():
                transaction.rollback()
            return sentry_exception_handler(request, **kwargs)

        exception_handler = wrap_sentry
    else:
        exception_handler = sentry_exception_handler
    got_request_exception.connect(exception_handler, weak=False)
    if u'djcelery' in settings.INSTALLED_APPS:
        try:
            from raven.contrib.celery import register_signal, register_logger_signal
        except ImportError:
            logger.exception(u'Failed to install Celery error handler')
        else:
            try:
                register_signal(client)
            except Exception:
                logger.exception(u'Failed to install Celery error handler')

            try:
                ga = lambda x, d = None: getattr(settings, u'SENTRY_%s' % x, d)
                options = getattr(settings, u'RAVEN_CONFIG', {})
                loglevel = options.get(u'celery_loglevel', ga(u'CELERY_LOGLEVEL', logging.ERROR))
                register_logger_signal(client, loglevel=loglevel)
            except Exception:
                logger.exception(u'Failed to install Celery error handler')


def register_serializers():
    import raven.contrib.django.serializers


if u'raven.contrib.django' in settings.INSTALLED_APPS or u'raven.contrib.django.raven_compat' in settings.INSTALLED_APPS:
    register_handlers()
    register_serializers()
