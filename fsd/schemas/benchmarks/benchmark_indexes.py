#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fsd\schemas\benchmarks\benchmark_indexes.py
import pyFSD
import time
import ctypes
import cPickle
import marshal
import fsd.schemas.validator as validator
import fsd.schemas.schemaOptimizer as schemaOptimizer
import fsd.schemas.binaryRepresenter as binaryRepresenter
import fsd.schemas.binaryLoader as binaryLoader
import fsd.schemas.loaders.dictLoader as dictLoader
schema = {'type': 'dict',
 'buildIndex': True,
 'keyTypes': {'type': 'int',
              'min': 0},
 'valueTypes': {'type': 'int'}}
optSchema = schemaOptimizer.OptimizeSchema(schema, validator.SERVER)
keySchema = optSchema['keyFooter']

def timeit(method):

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print '%r (%r, %r) %2.2f sec' % (method.__name__,
         args,
         kw,
         te - ts)
        return result

    return timed


offsets = []
COUNT = 500000
for i in xrange(COUNT):
    offsets.append({'key': i,
     'offset': 0,
     'size': 0})

offsetTableString = binaryRepresenter.RepresentAsBinary(offsets, keySchema, None)
print 'Timing %i item indexes' % COUNT

@timeit
def FsdUnsignedIntegerKeyMapLoadData():
    keyMap = pyFSD.FsdUnsignedIntegerKeyMap()
    keyMap.Initialize(offsetTableString)
    return dictLoader.CppFsdIntegerKeyMapWrapper(keyMap)


@timeit
def PythonFSDKeyMapLoadData():
    buff = ctypes.create_string_buffer(offsetTableString, len(offsetTableString))
    return dictLoader.StandardFSDDictFooter(buff, 0, keySchema, None, binaryLoader.LoaderState(binaryLoader.defaultLoaderFactories, None))


cppLookup = FsdUnsignedIntegerKeyMapLoadData()

@timeit
def FsdUnsignedIntegerKeyMapAccessAllElements():
    for i in xrange(COUNT):
        cppLookup.Get(i)


@timeit
def FsdUnsignedIntegerKeyMapAccessAllElementsWithoutAttrLookup():
    Get = cppLookup.Get
    for i in xrange(COUNT):
        Get(i)


FsdUnsignedIntegerKeyMapAccessAllElements()
FsdUnsignedIntegerKeyMapAccessAllElementsWithoutAttrLookup()

@timeit
def PythonFSDDataAccessAllElements():
    for i in xrange(COUNT):
        pythonLookup.Get(i)


dataAsDict = {}
for i in xrange(COUNT):
    dataAsDict[i] = (0, 0)

pickledData = cPickle.dumps(dataAsDict, protocol=cPickle.HIGHEST_PROTOCOL)

@timeit
def PythonDictLoadFromCPickle():
    return cPickle.loads(pickledData)


dataAsDict = PythonDictLoadFromCPickle()
marshalledData = marshal.dumps(dataAsDict)

@timeit
def PythonDictLoadFromMarshall():
    return marshal.loads(marshalledData)


PythonDictLoadFromMarshall()

@timeit
def PythonDictAccessAllElements():
    for i in xrange(COUNT):
        dataAsDict.get(i)


PythonDictAccessAllElements()
