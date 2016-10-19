#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fsd\mapReduce\debug.py


class FakeProcessPool(object):

    def __init__(self):
        pass

    def imap_unordered(self, fn, iterable, batchSize):
        for i in iterable:
            yield fn(i)

    def close(self):
        pass
