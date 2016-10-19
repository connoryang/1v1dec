#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\packages\urllib3\__init__.py
from __future__ import absolute_import
import warnings
from .connectionpool import HTTPConnectionPool, HTTPSConnectionPool, connection_from_url
from . import exceptions
from .filepost import encode_multipart_formdata
from .poolmanager import PoolManager, ProxyManager, proxy_from_url
from .response import HTTPResponse
from .util.request import make_headers
from .util.url import get_host
from .util.timeout import Timeout
from .util.retry import Retry
import logging
try:
    from logging import NullHandler
except ImportError:

    class NullHandler(logging.Handler):

        def emit(self, record):
            pass


__author__ = 'Andrey Petrov (andrey.petrov@shazow.net)'
__license__ = 'MIT'
__version__ = '1.15.1'
__all__ = ('HTTPConnectionPool', 'HTTPSConnectionPool', 'PoolManager', 'ProxyManager', 'HTTPResponse', 'Retry', 'Timeout', 'add_stderr_logger', 'connection_from_url', 'disable_warnings', 'encode_multipart_formdata', 'get_host', 'make_headers', 'proxy_from_url')
logging.getLogger(__name__).addHandler(NullHandler())

def add_stderr_logger(level = logging.DEBUG):
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.debug('Added a stderr logging handler to logger: %s', __name__)
    return handler


del NullHandler
warnings.simplefilter('always', exceptions.SecurityWarning, append=True)
warnings.simplefilter('default', exceptions.SubjectAltNameWarning, append=True)
warnings.simplefilter('default', exceptions.InsecurePlatformWarning, append=True)
warnings.simplefilter('default', exceptions.SNIMissingWarning, append=True)

def disable_warnings(category = exceptions.HTTPWarning):
    warnings.simplefilter('ignore', category)
