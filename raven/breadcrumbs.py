#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\breadcrumbs.py
from __future__ import absolute_import
import time
import logging
from types import FunctionType
from raven._compat import iteritems, get_code, text_type, string_types
from raven.utils import once
special_logger_handlers = {}
logger = logging.getLogger('raven')

def event_payload_considered_equal(a, b):
    return a['type'] == b['type'] and a['level'] == b['level'] and a['message'] == b['message'] and a['category'] == b['category'] and a['data'] == b['data']


class BreadcrumbBuffer(object):

    def __init__(self, limit = 100):
        self.buffer = []
        self.limit = limit

    def record(self, timestamp = None, level = None, message = None, category = None, data = None, type = None, processor = None):
        if not (message or data or processor):
            raise ValueError('You must pass either `message`, `data`, or `processor`')
        if timestamp is None:
            timestamp = time.time()
        self.buffer.append(({'type': type or 'default',
          'timestamp': timestamp,
          'level': level,
          'message': message,
          'category': category,
          'data': data}, processor))
        del self.buffer[:-self.limit]

    def clear(self):
        del self.buffer[:]

    def get_buffer(self):
        rv = []
        for idx, (payload, processor) in enumerate(self.buffer):
            if processor is not None:
                try:
                    processor(payload)
                except Exception:
                    logger.exception('Failed to process breadcrumbs. Ignored')
                    payload = None

                self.buffer[idx] = (payload, None)
            if payload is not None and (not rv or not event_payload_considered_equal(rv[-1], payload)):
                rv.append(payload)

        return rv


class BlackholeBreadcrumbBuffer(BreadcrumbBuffer):

    def record(self, *args, **kwargs):
        pass


def make_buffer(enabled = True):
    if enabled:
        return BreadcrumbBuffer()
    return BlackholeBreadcrumbBuffer()


def record_breadcrumb(type, *args, **kwargs):
    kwargs['type'] = type
    return record(*args, **kwargs)


def record(message = None, timestamp = None, level = None, category = None, data = None, type = None, processor = None):
    if timestamp is None:
        timestamp = time.time()
    for ctx in raven.context.get_active_contexts():
        ctx.breadcrumbs.record(timestamp, level, message, category, data, type, processor)


def _record_log_breadcrumb(logger, level, msg, *args, **kwargs):
    handler = special_logger_handlers.get(logger.name)
    if handler is not None:
        rv = handler(logger, level, msg, args, kwargs)
        if rv:
            return

    def processor(data):
        formatted_msg = msg
        try:
            formatted_msg = text_type(msg)
            if args:
                formatted_msg = msg % args
        except Exception:
            pass

        kwargs.pop('exc_info', None)
        data.update({'message': formatted_msg,
         'category': logger.name,
         'level': logging.getLevelName(level).lower(),
         'data': kwargs})

    record(processor=processor)


def _wrap_logging_method(meth, level = None):
    if not isinstance(meth, FunctionType):
        func = meth.im_func
    else:
        func = meth
    if getattr(func, '__patched_for_raven__', False):
        return
    if level is None:
        args = ('level', 'msg')
        fwd = 'level, msg'
    else:
        args = ('msg',)
        fwd = '%d, msg' % level
    code = get_code(func)
    ns = {}
    eval(compile('%(offset)sif 1:\n    def factory(original, record_crumb):\n        def %(name)s(self, %(args)s, *args, **kwargs):\n            record_crumb(self, %(fwd)s, *args, **kwargs)\n            return original(self, %(args)s, *args, **kwargs)\n        return %(name)s\n    \n' % {'offset': '\n' * (code.co_firstlineno - 3),
     'name': func.__name__,
     'args': ', '.join(args),
     'fwd': fwd,
     'level': level}, logging._srcfile, 'exec'), logging.__dict__, ns)
    new_func = ns['factory'](meth, _record_log_breadcrumb)
    new_func.__doc__ = func.__doc__
    new_func.__patched_for_raven__ = True
    return new_func


def _patch_logger():
    cls = logging.Logger
    methods = {'debug': logging.DEBUG,
     'info': logging.INFO,
     'warning': logging.WARNING,
     'warn': logging.WARN,
     'error': logging.ERROR,
     'exception': logging.ERROR,
     'critical': logging.CRITICAL,
     'fatal': logging.FATAL}
    for method_name, level in iteritems(methods):
        new_func = _wrap_logging_method(getattr(cls, method_name), level)
        setattr(logging.Logger, method_name, new_func)

    logging.Logger.log = _wrap_logging_method(logging.Logger.log)


@once
def install_logging_hook():
    _patch_logger()


def ignore_logger(name_or_logger, allow_level = None):

    def handler(logger, level, msg, args, kwargs):
        if allow_level is not None and level >= allow_level:
            return False
        return True

    register_special_log_handler(name_or_logger, handler)


def register_special_log_handler(name_or_logger, callback):
    if isinstance(name_or_logger, string_types):
        name = name_or_logger
    else:
        name = name_or_logger.name
    special_logger_handlers[name] = callback


hooked_libraries = {}

def libraryhook(name):

    def decorator(f):
        f = once(f)
        hooked_libraries[name] = f
        return f

    return decorator


@libraryhook('requests')
def _hook_requests():
    try:
        from requests.sessions import Session
    except ImportError:
        return

    real_send = Session.send

    def send(self, request, *args, **kwargs):

        def _record_request(response):
            record(type='http', category='requests', data={'url': request.url,
             'method': request.method,
             'status_code': response and response.status_code or None,
             'reason': response and response.reason or None})

        try:
            resp = real_send(self, request, *args, **kwargs)
        except Exception:
            _record_request(None)
            raise
        else:
            _record_request(resp)

        return resp

    Session.send = send
    ignore_logger('requests.packages.urllib3.connectionpool', allow_level=logging.WARNING)


@libraryhook('httplib')
def _install_httplib():
    try:
        from httplib import HTTPConnection
    except ImportError:
        from http.client import HTTPConnection

    real_putrequest = HTTPConnection.putrequest
    real_getresponse = HTTPConnection.getresponse

    def putrequest(self, method, url, *args, **kwargs):
        self._raven_status_dict = status = {}
        host = self.host
        port = self.port
        default_port = self.default_port

        def processor(data):
            real_url = url
            if not real_url.startswith(('http://', 'https://')):
                real_url = '%s://%s%s%s' % (default_port == 443 and 'https' or 'http',
                 host,
                 port != default_port and ':%s' % port or '',
                 url)
            data['data'] = {'url': real_url,
             'method': method}
            data['data'].update(status)
            return data

        record(type='http', category='requests', processor=processor)
        return real_putrequest(self, method, url, *args, **kwargs)

    def getresponse(self, *args, **kwargs):
        rv = real_getresponse(self, *args, **kwargs)
        status = getattr(self, '_raven_status_dict', None)
        if status is not None and 'status_code' not in status:
            status['status_code'] = rv.status
            status['reason'] = rv.reason
        return rv

    HTTPConnection.putrequest = putrequest
    HTTPConnection.getresponse = getresponse


def hook_libraries(libraries):
    if libraries is None:
        libraries = hooked_libraries.keys()
    for lib in libraries:
        func = hooked_libraries.get(lib)
        if func is None:
            raise RuntimeError('Unknown library %r for hooking' % lib)
        func()


import raven.context
