#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\__init__.py
__title__ = 'requests'
__version__ = '2.10.0'
__build__ = 135168
__author__ = 'Kenneth Reitz'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2016 Kenneth Reitz'
try:
    from .packages.urllib3.contrib import pyopenssl
    pyopenssl.inject_into_urllib3()
except ImportError:
    pass

import warnings
from .packages.urllib3.exceptions import DependencyWarning
warnings.simplefilter('ignore', DependencyWarning)
from . import utils
from .models import Request, Response, PreparedRequest
from .api import request, get, head, post, patch, put, delete, options
from .sessions import session, Session
from .status_codes import codes
from .exceptions import RequestException, Timeout, URLRequired, TooManyRedirects, HTTPError, ConnectionError, FileModeWarning, ConnectTimeout, ReadTimeout
import logging
try:
    from logging import NullHandler
except ImportError:

    class NullHandler(logging.Handler):

        def emit(self, record):
            pass


logging.getLogger(__name__).addHandler(NullHandler())
import warnings
warnings.simplefilter('default', FileModeWarning, append=True)
