#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fsd\schemas\benchmarks\benchmark_general.py
import benchmarkUtil
import fsd.schemas.schemaOptimizer as schemaOptimizer
import fsd.schemas.binaryRepresenter as binaryRepresenter
import fsd.schemas.binaryLoader as binaryLoader
OBJECT_READ_COUNT = 400000
_podObjectSchema = {'type': 'object',
 'attributes': {'foo': {'type': 'int'},
                'bar': {'type': 'float'}}}
_podObjectOptSchema = schemaOptimizer.OptimizeSchema(_podObjectSchema, 'Client')
_podObjectEncoded = binaryRepresenter.RepresentAsBinary({'foo': 1,
 'bar': 0.2}, _podObjectOptSchema)

@benchmarkUtil.benchmark
def BenchmarkPODObjectReading():
    for i in xrange(OBJECT_READ_COUNT):
        _ = binaryLoader.LoadFromString(_podObjectEncoded, _podObjectOptSchema)


loadedPod = binaryLoader.LoadFromString(_podObjectEncoded, _podObjectOptSchema)

@benchmarkUtil.benchmark
def BenchmarkPODObjectAccess():
    for i in xrange(OBJECT_READ_COUNT):
        _ = loadedPod.foo


_complexObjectSchema = {'type': 'object',
 'attributes': {'name': {'type': 'string'},
                'bar': {'type': 'float'},
                'items': {'type': 'list',
                          'sortOrder': 'Ascending',
                          'itemTypes': {'type': 'int'}}}}
_complexObjectOptSchema = schemaOptimizer.OptimizeSchema(_complexObjectSchema, 'Client')
_complexObjectEncoded = binaryRepresenter.RepresentAsBinary({'name': 'foober',
 'bar': 0.2,
 'items': [1,
           2,
           3,
           4]}, _complexObjectOptSchema)
import cProfile, pstats, io
import cStringIO
loadedComplex = binaryLoader.LoadFromString(_complexObjectEncoded, _complexObjectOptSchema)

@benchmarkUtil.benchmark
def BenchmarkComplexObjectAccess():
    for i in xrange(OBJECT_READ_COUNT):
        _ = loadedComplex.name


_complexDictObjectSchema = {'type': 'dict',
 'buildIndex': True,
 'keyTypes': {'type': 'int'},
 'valueTypes': {'type': 'object',
                'attributes': {'name': {'type': 'string'},
                               'bar': {'type': 'float'}}}}
DICT_LOOKUP_COUNT = 400000
_complexDictObjectOptSchema = schemaOptimizer.OptimizeSchema(_complexDictObjectSchema, 'Client')
_complexDictObjectEncoded = binaryRepresenter.RepresentAsBinary({i:{'name': 'foober',
 'bar': 0.2} for i in xrange(DICT_LOOKUP_COUNT)}, _complexDictObjectOptSchema)
dictLoaded = binaryLoader.LoadIndexFromFile(cStringIO.StringIO(_complexDictObjectEncoded), _complexDictObjectOptSchema)
PROFILE = False

@benchmarkUtil.benchmark
def BenchmarkComplexObjectAccessInDict():
    if PROFILE:
        pr = cProfile.Profile()
        pr.enable()
    for i in xrange(DICT_LOOKUP_COUNT):
        _ = dictLoaded[i].name

    if PROFILE:
        pr.disable()
        s = io.StringIO()
        ps = pstats.Stats(pr)
        ps.sort_stats('cumulative')
        ps.print_stats()
        ps.print_callees('__getitem__')
        ps.print_callees('__init__')


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    benchmarkUtil.RunRegisteredBenchmarks('runs.log')
