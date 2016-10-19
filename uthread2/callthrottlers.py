#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\uthread2\callthrottlers.py
from . import sleep, start_tasklet

class CallCombiner(object):

    def __init__(self, func, throttleTime):
        self.isBeingCalled = False
        self.func = func
        self.throttleTime = throttleTime

    def __call__(self, *args, **kwargs):
        if self.isBeingCalled:
            return
        self.isBeingCalled = True
        try:
            sleep(self.throttleTime)
            return self.func(*args, **kwargs)
        finally:
            self.isBeingCalled = False


def BufferedCall(delay = 1000):

    def BufferedCallDecorator(method):
        method._buffering = False

        def BufferedCallThread(*args, **kwargs):
            try:
                sleep(delay / 1000.0)
                method(*args, **kwargs)
            finally:
                method._buffering = False

        def BufferedCallWrapper(*args, **kwargs):
            if method._buffering is False:
                method._buffering = True
                start_tasklet(BufferedCallThread, *args, **kwargs)

        return BufferedCallWrapper

    return BufferedCallDecorator
