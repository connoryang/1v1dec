#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fsd\schemas\benchmarks\benchmarkDictOffsetDataLookup.py
__author__ = 'baering'
import benchmarkUtil
from fsd.schemas.nestedIndexedOffsetData import IndexedOffsetData
import fsd.schemas.binaryRepresenter as binaryRepresenter
from fsd.schemas.loaders import readBinaryDataFromFileAtOffset, readIntFromBinaryStringAtOffset, readIntFromFileAtOffset
from fsd.schemas.loaders.dictLoader import StandardFSDOptimizedDictFooter, StandardFSDDictFooter
import fsd.schemas.binaryLoader as binaryLoader
import fsd.schemas.schemaOptimizer as schemaOptimizer
import fsd.schemas.validator as validator
import ctypes
import logging
log = logging.getLogger(__name__)
size = 100000
schema = {'type': 'dict',
 'buildIndex': True,
 'keyTypes': {'type': 'int'},
 'valueTypes': {'type': 'int'}}
optSchema = schemaOptimizer.OptimizeSchema(schema, validator.SERVER)

def CreateUnOptimizedOffsetData(key, offset, size):
    return {'key': key,
     'offset': offset,
     'size': size}


def CreateOptimizedOffsetData(key, offset, size):
    return (key, offset, size)


def CreateStandardFSDDictFooter():
    offsetData = [ CreateUnOptimizedOffsetData(x, x * 2, x * 3) for x in range(1, size + 1) ]
    binaryOffsetDataTable = binaryRepresenter.RepresentAsBinary(offsetData, optSchema['keyFooter'])
    return StandardFSDDictFooter(ctypes.create_string_buffer(binaryOffsetDataTable, len(binaryOffsetDataTable)), 0, optSchema['keyFooter'], 'Benchmark Testing', binaryLoader.LoaderState(binaryLoader.defaultLoaderFactories, None))


def CreateStandardFSDOptimizedDictFooter():
    offsetData = [ CreateUnOptimizedOffsetData(x, x * 2, x * 3) for x in range(1, size + 1) ]
    binaryOffsetDataTable = binaryRepresenter.RepresentAsBinary(offsetData, optSchema['keyFooter'])
    return StandardFSDOptimizedDictFooter(ctypes.create_string_buffer(binaryOffsetDataTable, len(binaryOffsetDataTable)), optSchema)


unoptimizedDictFooter = CreateStandardFSDDictFooter()
optimizedDictFooter = CreateStandardFSDOptimizedDictFooter()

@benchmarkUtil.benchmark
def SearchInUnoptimizedData():
    print 'Result:', unoptimizedDictFooter.Get(1)


@benchmarkUtil.benchmark
def SearchInOptimizedData():
    print 'Result:', optimizedDictFooter.Get(1)


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    benchmarkUtil.RunRegisteredBenchmarks('dictOffsetDataLookup_benchmark.log')
