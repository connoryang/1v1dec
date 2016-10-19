#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\ccpraven\__init__.py
import __builtin__
import logging
from raven import Client
from raven.conf import setup_logging
import raven.breadcrumbs
from .session_proxy import RequestsSessionProxyHTTPTransport
from .handlers import CcpHandler
client = None
processors = ('raven.processors.SanitizePasswordsProcessor', 'ccpraven.processors.EveSessionProcessor')

def raven_client(dsn, release, tags, environment, context, ignore_exceptions):
    global client
    if client is None:
        client = Client(dsn=dsn, transport=RequestsSessionProxyHTTPTransport, release=release, tags=tags, environment=environment, context=context, processors=processors, ignore_exceptions=ignore_exceptions)
        raven.breadcrumbs.ignore_logger('raven.base.Client', allow_level=logging.WARNING)
        handler = CcpHandler(client, level=logging.ERROR, ignore_exceptions=ignore_exceptions)
        setup_logging(handler)
        logging.getLogger('raven').setLevel(logging.ERROR)
    return client


def capture_exception(message, exc_info = None):
    if client is None:
        return
    extra = {'original_message': message}
    if exc_info is None or exc_info == (None, None, None):
        client.captureMessage('LogException used without except block', stack=True, extra=extra)
        return
    client.captureException(message=message)
