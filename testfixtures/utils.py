#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\testfixtures\utils.py
from functools import wraps
from inspect import getargspec

def generator(*args):
    for i in args:
        yield i


class Wrappings:

    def __init__(self):
        self.before = []
        self.after = []


def wrap(before, after = None):

    def wrapper(wrapped):
        if getattr(wrapped, '_wrappings', None) is None:
            w = Wrappings()

            @wraps(wrapped)
            def wrapping(*args, **kw):
                args = list(args)
                to_add = len(getargspec(wrapped)[0][len(args):])
                added = 0
                for c in w.before:
                    r = c()
                    if added < to_add:
                        args.append(r)
                        added += 1

                try:
                    return wrapped(*args, **kw)
                finally:
                    for c in w.after:
                        c()

            f = wrapping
            f._wrappings = w
        else:
            f = wrapped
        w = f._wrappings
        w.before.append(before)
        if after is not None:
            w.after.insert(0, after)
        return f

    return wrapper
