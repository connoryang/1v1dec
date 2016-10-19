#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\testfixtures\shouldraise.py
from functools import wraps
from testfixtures import Comparison
param_docs = '\n\n    :param exception: This can be one of the following:\n\n                      * `None`, indicating that an exception must be\n                        raised, but the type is unimportant.\n\n                      * An exception class, indicating that the type\n                        of the exception is important but not the\n                        parameters it is created with.\n\n                      * An exception instance, indicating that an\n                        exception exactly matching the one supplied\n                        should be raised.\n\n    :param unless: Can be passed a boolean that, when ``True`` indicates that\n                   no exception is expected. This is useful when checking\n                   that exceptions are only raised on certain versions of\n                   Python.\n'

class ShouldRaise(object):
    __doc__ = '\n    This context manager is used to assert that an exception is raised\n    within the context it is managing.\n    ' + param_docs
    raised = None

    def __init__(self, exception = None, unless = False):
        self.exception = exception
        self.expected = not unless

    def __enter__(self):
        return self

    def __exit__(self, type, actual, traceback):
        if type is not None and not isinstance(actual, type):
            actual = type(actual)
        self.raised = actual
        if self.expected:
            if self.exception:
                comparison = Comparison(self.exception)
                if comparison != actual:
                    repr_actual = repr(actual)
                    repr_expected = repr(self.exception)
                    message = '%s raised, %s expected' % (repr_actual, repr_expected)
                    if repr_actual == repr_expected:
                        print str(comparison).split('\n')
                        extra = [', attributes differ:']
                        extra.extend(str(comparison).split('\n')[2:-1])
                        message += '\n'.join(extra)
                    raise AssertionError(message)
            elif not actual:
                raise AssertionError('No exception raised!')
        elif actual:
            raise AssertionError('%r raised, no exception expected' % actual)
        return True


class should_raise:
    __doc__ = '\n    A decorator to assert that the decorated function will raised\n    an exception. An exception class or exception instance may be\n    passed to check more specifically exactly what exception will be\n    raised.\n    ' + param_docs

    def __init__(self, exception = None, unless = None):
        self.exception = exception
        self.unless = unless

    def __call__(self, target):

        @wraps(target)
        def _should_raise_wrapper(*args, **kw):
            with ShouldRaise(self.exception, self.unless):
                target(*args, **kw)

        return _should_raise_wrapper
