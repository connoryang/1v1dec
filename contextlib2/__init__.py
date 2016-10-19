#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\contextlib2\__init__.py
import sys
import warnings
from collections import deque
from functools import wraps
__all__ = ['contextmanager',
 'closing',
 'ContextDecorator',
 'ExitStack',
 'redirect_stdout',
 'redirect_stderr',
 'suppress']
__all__ += ['ContextStack']

class ContextDecorator(object):

    def refresh_cm(self):
        warnings.warn('refresh_cm was never added to the standard library', DeprecationWarning)
        return self._recreate_cm()

    def _recreate_cm(self):
        return self

    def __call__(self, func):

        @wraps(func)
        def inner(*args, **kwds):
            with self._recreate_cm():
                return func(*args, **kwds)

        return inner


class _GeneratorContextManager(ContextDecorator):

    def __init__(self, func, args, kwds):
        self.gen = func(*args, **kwds)
        self.func, self.args, self.kwds = func, args, kwds
        doc = getattr(func, '__doc__', None)
        if doc is None:
            doc = type(self).__doc__
        self.__doc__ = doc

    def _recreate_cm(self):
        return self.__class__(self.func, self.args, self.kwds)

    def __enter__(self):
        try:
            return next(self.gen)
        except StopIteration:
            raise RuntimeError("generator didn't yield")

    def __exit__(self, type, value, traceback):
        if type is None:
            try:
                next(self.gen)
            except StopIteration:
                return

            raise RuntimeError("generator didn't stop")
        else:
            if value is None:
                value = type()
            try:
                self.gen.throw(type, value, traceback)
                raise RuntimeError("generator didn't stop after throw()")
            except StopIteration as exc:
                return exc is not value
            except RuntimeError as exc:
                if exc is value:
                    return False
                if _HAVE_EXCEPTION_CHAINING and exc.__cause__ is value:
                    return False
                raise
            except:
                if sys.exc_info()[1] is not value:
                    raise


def contextmanager(func):

    @wraps(func)
    def helper(*args, **kwds):
        return _GeneratorContextManager(func, args, kwds)

    return helper


class closing(object):

    def __init__(self, thing):
        self.thing = thing

    def __enter__(self):
        return self.thing

    def __exit__(self, *exc_info):
        self.thing.close()


class _RedirectStream(object):
    _stream = None

    def __init__(self, new_target):
        self._new_target = new_target
        self._old_targets = []

    def __enter__(self):
        self._old_targets.append(getattr(sys, self._stream))
        setattr(sys, self._stream, self._new_target)
        return self._new_target

    def __exit__(self, exctype, excinst, exctb):
        setattr(sys, self._stream, self._old_targets.pop())


class redirect_stdout(_RedirectStream):
    _stream = 'stdout'


class redirect_stderr(_RedirectStream):
    _stream = 'stderr'


class suppress(object):

    def __init__(self, *exceptions):
        self._exceptions = exceptions

    def __enter__(self):
        pass

    def __exit__(self, exctype, excinst, exctb):
        return exctype is not None and issubclass(exctype, self._exceptions)


_HAVE_EXCEPTION_CHAINING = sys.version_info[0] >= 3
if _HAVE_EXCEPTION_CHAINING:

    def _make_context_fixer(frame_exc):

        def _fix_exception_context(new_exc, old_exc):
            while 1:
                exc_context = new_exc.__context__
                if exc_context is old_exc:
                    return
                if exc_context is None or exc_context is frame_exc:
                    break
                new_exc = exc_context

            new_exc.__context__ = old_exc

        return _fix_exception_context


    def _reraise_with_existing_context(exc_details):
        try:
            fixed_ctx = exc_details[1].__context__
            raise exc_details[1]
        except BaseException:
            exc_details[1].__context__ = fixed_ctx
            raise


else:

    def _make_context_fixer(frame_exc):
        return lambda new_exc, old_exc: None


    def _reraise_with_existing_context(exc_details):
        exc_type, exc_value, exc_tb = exc_details
        exec 'raise exc_type, exc_value, exc_tb'


try:
    from types import InstanceType
except ImportError:
    _get_type = type
else:

    def _get_type(obj):
        obj_type = type(obj)
        if obj_type is InstanceType:
            return obj.__class__
        return obj_type


class ExitStack(object):

    def __init__(self):
        self._exit_callbacks = deque()

    def pop_all(self):
        new_stack = type(self)()
        new_stack._exit_callbacks = self._exit_callbacks
        self._exit_callbacks = deque()
        return new_stack

    def _push_cm_exit(self, cm, cm_exit):

        def _exit_wrapper(*exc_details):
            return cm_exit(cm, *exc_details)

        _exit_wrapper.__self__ = cm
        self.push(_exit_wrapper)

    def push(self, exit):
        _cb_type = _get_type(exit)
        try:
            exit_method = _cb_type.__exit__
        except AttributeError:
            self._exit_callbacks.append(exit)
        else:
            self._push_cm_exit(exit, exit_method)

        return exit

    def callback(self, callback, *args, **kwds):

        def _exit_wrapper(exc_type, exc, tb):
            callback(*args, **kwds)

        _exit_wrapper.__wrapped__ = callback
        self.push(_exit_wrapper)
        return callback

    def enter_context(self, cm):
        _cm_type = _get_type(cm)
        _exit = _cm_type.__exit__
        result = _cm_type.__enter__(cm)
        self._push_cm_exit(cm, _exit)
        return result

    def close(self):
        self.__exit__(None, None, None)

    def __enter__(self):
        return self

    def __exit__(self, *exc_details):
        received_exc = exc_details[0] is not None
        frame_exc = sys.exc_info()[1]
        _fix_exception_context = _make_context_fixer(frame_exc)
        suppressed_exc = False
        pending_raise = False
        while self._exit_callbacks:
            cb = self._exit_callbacks.pop()
            try:
                if cb(*exc_details):
                    suppressed_exc = True
                    pending_raise = False
                    exc_details = (None, None, None)
            except:
                new_exc_details = sys.exc_info()
                _fix_exception_context(new_exc_details[1], exc_details[1])
                pending_raise = True
                exc_details = new_exc_details

        if pending_raise:
            _reraise_with_existing_context(exc_details)
        return received_exc and suppressed_exc


class ContextStack(ExitStack):

    def __init__(self):
        warnings.warn('ContextStack has been renamed to ExitStack', DeprecationWarning)
        super(ContextStack, self).__init__()

    def register_exit(self, callback):
        return self.push(callback)

    def register(self, callback, *args, **kwds):
        return self.callback(callback, *args, **kwds)

    def preserve(self):
        return self.pop_all()
