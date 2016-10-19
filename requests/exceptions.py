#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\exceptions.py
from .packages.urllib3.exceptions import HTTPError as BaseHTTPError

class RequestException(IOError):

    def __init__(self, *args, **kwargs):
        response = kwargs.pop('response', None)
        self.response = response
        self.request = kwargs.pop('request', None)
        if response is not None and not self.request and hasattr(response, 'request'):
            self.request = self.response.request
        super(RequestException, self).__init__(*args, **kwargs)


class HTTPError(RequestException):
    pass


class ConnectionError(RequestException):
    pass


class ProxyError(ConnectionError):
    pass


class SSLError(ConnectionError):
    pass


class Timeout(RequestException):
    pass


class ConnectTimeout(ConnectionError, Timeout):
    pass


class ReadTimeout(Timeout):
    pass


class URLRequired(RequestException):
    pass


class TooManyRedirects(RequestException):
    pass


class MissingSchema(RequestException, ValueError):
    pass


class InvalidSchema(RequestException, ValueError):
    pass


class InvalidURL(RequestException, ValueError):
    pass


class ChunkedEncodingError(RequestException):
    pass


class ContentDecodingError(RequestException, BaseHTTPError):
    pass


class StreamConsumedError(RequestException, TypeError):
    pass


class RetryError(RequestException):
    pass


class RequestsWarning(Warning):
    pass


class FileModeWarning(RequestsWarning, DeprecationWarning):
    pass
