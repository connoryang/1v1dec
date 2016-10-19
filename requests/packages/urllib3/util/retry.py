#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\packages\urllib3\util\retry.py
from __future__ import absolute_import
import time
import logging
from ..exceptions import ConnectTimeoutError, MaxRetryError, ProtocolError, ReadTimeoutError, ResponseError
from ..packages import six
log = logging.getLogger(__name__)

class Retry(object):
    DEFAULT_METHOD_WHITELIST = frozenset(['HEAD',
     'GET',
     'PUT',
     'DELETE',
     'OPTIONS',
     'TRACE'])
    BACKOFF_MAX = 120

    def __init__(self, total = 10, connect = None, read = None, redirect = None, method_whitelist = DEFAULT_METHOD_WHITELIST, status_forcelist = None, backoff_factor = 0, raise_on_redirect = True, raise_on_status = True, _observed_errors = 0):
        self.total = total
        self.connect = connect
        self.read = read
        if redirect is False or total is False:
            redirect = 0
            raise_on_redirect = False
        self.redirect = redirect
        self.status_forcelist = status_forcelist or set()
        self.method_whitelist = method_whitelist
        self.backoff_factor = backoff_factor
        self.raise_on_redirect = raise_on_redirect
        self.raise_on_status = raise_on_status
        self._observed_errors = _observed_errors

    def new(self, **kw):
        params = dict(total=self.total, connect=self.connect, read=self.read, redirect=self.redirect, method_whitelist=self.method_whitelist, status_forcelist=self.status_forcelist, backoff_factor=self.backoff_factor, raise_on_redirect=self.raise_on_redirect, raise_on_status=self.raise_on_status, _observed_errors=self._observed_errors)
        params.update(kw)
        return type(self)(**params)

    @classmethod
    def from_int(cls, retries, redirect = True, default = None):
        if retries is None:
            retries = default if default is not None else cls.DEFAULT
        if isinstance(retries, Retry):
            return retries
        redirect = bool(redirect) and None
        new_retries = cls(retries, redirect=redirect)
        log.debug('Converted retries value: %r -> %r', retries, new_retries)
        return new_retries

    def get_backoff_time(self):
        if self._observed_errors <= 1:
            return 0
        backoff_value = self.backoff_factor * 2 ** (self._observed_errors - 1)
        return min(self.BACKOFF_MAX, backoff_value)

    def sleep(self):
        backoff = self.get_backoff_time()
        if backoff <= 0:
            return
        time.sleep(backoff)

    def _is_connection_error(self, err):
        return isinstance(err, ConnectTimeoutError)

    def _is_read_error(self, err):
        return isinstance(err, (ReadTimeoutError, ProtocolError))

    def is_forced_retry(self, method, status_code):
        if self.method_whitelist and method.upper() not in self.method_whitelist:
            return False
        return self.status_forcelist and status_code in self.status_forcelist

    def is_exhausted(self):
        retry_counts = (self.total,
         self.connect,
         self.read,
         self.redirect)
        retry_counts = list(filter(None, retry_counts))
        if not retry_counts:
            return False
        return min(retry_counts) < 0

    def increment(self, method = None, url = None, response = None, error = None, _pool = None, _stacktrace = None):
        if self.total is False and error:
            raise six.reraise(type(error), error, _stacktrace)
        total = self.total
        if total is not None:
            total -= 1
        _observed_errors = self._observed_errors
        connect = self.connect
        read = self.read
        redirect = self.redirect
        cause = 'unknown'
        if error and self._is_connection_error(error):
            if connect is False:
                raise six.reraise(type(error), error, _stacktrace)
            elif connect is not None:
                connect -= 1
            _observed_errors += 1
        elif error and self._is_read_error(error):
            if read is False:
                raise six.reraise(type(error), error, _stacktrace)
            elif read is not None:
                read -= 1
            _observed_errors += 1
        elif response and response.get_redirect_location():
            if redirect is not None:
                redirect -= 1
            cause = 'too many redirects'
        else:
            _observed_errors += 1
            cause = ResponseError.GENERIC_ERROR
            if response and response.status:
                cause = ResponseError.SPECIFIC_ERROR.format(status_code=response.status)
        new_retry = self.new(total=total, connect=connect, read=read, redirect=redirect, _observed_errors=_observed_errors)
        if new_retry.is_exhausted():
            raise MaxRetryError(_pool, url, error or ResponseError(cause))
        log.debug("Incremented Retry for (url='%s'): %r", url, new_retry)
        return new_retry

    def __repr__(self):
        return '{cls.__name__}(total={self.total}, connect={self.connect}, read={self.read}, redirect={self.redirect})'.format(cls=type(self), self=self)


Retry.DEFAULT = Retry(3)
