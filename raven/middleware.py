#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\middleware.py
from __future__ import absolute_import
from contextlib import contextmanager
from raven._compat import Iterator, next
from raven.utils.wsgi import get_current_url, get_headers, get_environ

@contextmanager
def common_exception_handling(environ, client):
    try:
        yield
    except (StopIteration, GeneratorExit):
        raise
    except Exception:
        client.handle_exception(environ)
        raise
    except KeyboardInterrupt:
        client.handle_exception(environ)
        raise
    except SystemExit as e:
        if e.code != 0:
            client.handle_exception(environ)
        raise


class ClosingIterator(Iterator):

    def __init__(self, sentry, iterable, environ):
        self.sentry = sentry
        self.environ = environ
        self.iterable = iter(iterable)

    def __iter__(self):
        return self

    def __next__(self):
        with common_exception_handling(self.environ, self.sentry):
            return next(self.iterable)

    def close(self):
        try:
            if hasattr(self.iterable, 'close'):
                with common_exception_handling(self.environ, self.sentry):
                    self.iterable.close()
        finally:
            self.sentry.client.context.clear()


class Sentry(object):

    def __init__(self, application, client = None):
        self.application = application
        if client is None:
            from raven.base import Client
            client = Client()
        self.client = client

    def __call__(self, environ, start_response):
        self.client.http_context(self.get_http_context(environ))
        with common_exception_handling(environ, self):
            iterable = self.application(environ, start_response)
        return ClosingIterator(self, iterable, environ)

    def get_http_context(self, environ):
        return {'method': environ.get('REQUEST_METHOD'),
         'url': get_current_url(environ, strip_querystring=True),
         'query_string': environ.get('QUERY_STRING'),
         'headers': dict(get_headers(environ)),
         'env': dict(get_environ(environ))}

    def process_response(self, request, response):
        self.client.context.clear()

    def handle_exception(self, environ = None):
        return self.client.captureException()
