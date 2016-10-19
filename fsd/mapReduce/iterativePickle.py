#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fsd\mapReduce\iterativePickle.py
import cPickle
import struct
lenint = struct.Struct('I')

class IterativePickleWithHeaderObject(object):

    @staticmethod
    def WriteIterableWithHeaderAndLengthAsIterativePickle(fileobject, headerObject, length, iterable):
        if headerObject is None:
            fileobject.write(lenint.pack(0))
        else:
            p = cPickle.dumps(headerObject)
            fileobject.write(lenint.pack(len(p)))
            fileobject.write(p)
        fileobject.write(lenint.pack(length))
        for item in iterable:
            pickledItem = cPickle.dumps(item)
            fileobject.write(lenint.pack(len(pickledItem)))
            fileobject.write(pickledItem)

    def __init__(self, filename_or_object):
        if isinstance(filename_or_object, basestring):
            self.file = open(filename_or_object, 'rb')
        else:
            self.file = filename_or_object
        headerSize = lenint.unpack(self.file.read(lenint.size))[0]
        if headerSize:
            self.header = cPickle.loads(self.file.read(headerSize))
        else:
            self.header = None
        self.fp = self.file.tell()
        s = self.file.read(lenint.size)
        self.length = lenint.unpack(s)[0]
        self.idx = 0
        self.isOpen = True

    def __iter__(self):
        return self

    def next(self):
        if self.idx == self.length:
            self.file.close()
            self.isOpen = False
            raise StopIteration
        else:
            self.idx += 1
            nextItemLen = lenint.unpack(self.file.read(lenint.size))[0]
            return cPickle.loads(self.file.read(nextItemLen))

    def __len__(self):
        return self.length

    def __del__(self):
        if self.isOpen:
            self.file.close()
