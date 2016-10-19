#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\packages\urllib3\exceptions.py
from __future__ import absolute_import

class HTTPError(Exception):
    pass


class HTTPWarning(Warning):
    pass


class PoolError(HTTPError):

    def __init__(self, pool, message):
        self.pool = pool
        HTTPError.__init__(self, '%s: %s' % (pool, message))

    def __reduce__(self):
        return (self.__class__, (None, None))


class RequestError(PoolError):

    def __init__(self, pool, url, message):
        self.url = url
        PoolError.__init__(self, pool, message)

    def __reduce__(self):
        return (self.__class__, (None, self.url, None))


class SSLError(HTTPError):
    pass


class ProxyError(HTTPError):
    pass


class DecodeError(HTTPError):
    pass


class ProtocolError(HTTPError):
    pass


ConnectionError = ProtocolError

class MaxRetryError(RequestError):

    def __init__(self, pool, url, reason = None):
        self.reason = reason
        message = 'Max retries exceeded with url: %s (Caused by %r)' % (url, reason)
        RequestError.__init__(self, pool, url, message)


class HostChangedError(RequestError):

    def __init__(self, pool, url, retries = 3):
        message = 'Tried to open a foreign host with url: %s' % url
        RequestError.__init__(self, pool, url, message)
        self.retries = retries


class TimeoutStateError(HTTPError):
    pass


class TimeoutError(HTTPError):
    pass


class ReadTimeoutError(TimeoutError, RequestError):
    pass


class ConnectTimeoutError(TimeoutError):
    pass


class NewConnectionError(ConnectTimeoutError, PoolError):
    pass


class EmptyPoolError(PoolError):
    pass


class ClosedPoolError(PoolError):
    pass


class LocationValueError(ValueError, HTTPError):
    pass


class LocationParseError(LocationValueError):

    def __init__(self, location):
        message = 'Failed to parse: %s' % location
        HTTPError.__init__(self, message)
        self.location = location


class ResponseError(HTTPError):
    GENERIC_ERROR = 'too many error responses'
    SPECIFIC_ERROR = 'too many {status_code} error responses'


class SecurityWarning(HTTPWarning):
    pass


class SubjectAltNameWarning(SecurityWarning):
    pass


class InsecureRequestWarning(SecurityWarning):
    pass


class SystemTimeWarning(SecurityWarning):
    pass


class InsecurePlatformWarning(SecurityWarning):
    pass


class SNIMissingWarning(HTTPWarning):
    pass


class DependencyWarning(HTTPWarning):
    pass


class ResponseNotChunked(ProtocolError, ValueError):
    pass


class ProxySchemeUnknown(AssertionError, ValueError):

    def __init__(self, scheme):
        message = 'Not supported proxy scheme %s' % scheme
        super(ProxySchemeUnknown, self).__init__(message)


class HeaderParsingError(HTTPError):

    def __init__(self, defects, unparsed_data):
        message = '%s, unparsed data: %r' % (defects or 'Unknown', unparsed_data)
        super(HeaderParsingError, self).__init__(message)
