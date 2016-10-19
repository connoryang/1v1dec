#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\testfixtures\logcapture.py
from collections import defaultdict
import atexit
import logging
import warnings
from testfixtures.comparison import compare
from testfixtures.utils import wrap

class LogCapture(logging.Handler):
    instances = set()
    atexit_setup = False
    installed = False

    def __init__(self, names = None, install = True, level = 1, propagate = None):
        logging.Handler.__init__(self)
        if not isinstance(names, tuple):
            names = (names,)
        self.names = names
        self.level = level
        self.propagate = propagate
        self.old = defaultdict(dict)
        self.clear()
        if install:
            self.install()

    @classmethod
    def atexit(cls):
        if cls.instances:
            warnings.warn('LogCapture instances not uninstalled by shutdown, loggers captured:\n%s' % '\n'.join((str(i.names) for i in cls.instances)))

    def clear(self):
        self.records = []

    def emit(self, record):
        self.records.append(record)

    def install(self):
        for name in self.names:
            logger = logging.getLogger(name)
            self.old['levels'][name] = logger.level
            self.old['handlers'][name] = logger.handlers
            self.old['disabled'][name] = logger.disabled
            self.old['progagate'][name] = logger.propagate
            logger.setLevel(self.level)
            logger.handlers = [self]
            logger.disabled = False
            if self.propagate is not None:
                logger.propagate = self.propagate

        self.instances.add(self)
        if not self.__class__.atexit_setup:
            atexit.register(self.atexit)
            self.__class__.atexit_setup = True

    def uninstall(self):
        if self in self.instances:
            for name in self.names:
                logger = logging.getLogger(name)
                logger.setLevel(self.old['levels'][name])
                logger.handlers = self.old['handlers'][name]
                logger.disabled = self.old['disabled'][name]
                logger.propagate = self.old['progagate'][name]

            self.instances.remove(self)

    @classmethod
    def uninstall_all(cls):
        for i in tuple(cls.instances):
            i.uninstall()

    def actual(self):
        for r in self.records:
            yield (r.name, r.levelname, r.getMessage())

    def __str__(self):
        if not self.records:
            return 'No logging captured'
        return '\n'.join([ '%s %s\n  %s' % r for r in self.actual() ])

    def check(self, *expected):
        return compare(expected, actual=tuple(self.actual()), recursive=False)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.uninstall()


class LogCaptureForDecorator(LogCapture):

    def install(self):
        LogCapture.install(self)
        return self


def log_capture(*names, **kw):
    l = LogCaptureForDecorator((names or None), install=False, **kw)
    return wrap(l.install, l.uninstall)
