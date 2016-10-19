#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fsd\schemas\benchmarks\benchmark_nesteIndexOffsetData.py
__author__ = 'olafurth'
import benchmarkUtil
from fsd.schemas.nestedIndexedOffsetData import IndexedOffsetData
COUNT = 150000

def CreateIndexedOffsetDataset():
    indexedOffsetData = IndexedOffsetData()
    for i in range(0, COUNT):
        iod = IndexedOffsetData(i * 10)
        iod.AddKeyOffsetSizeAndPathToNestedIndexId(i, 10, 10, 'path', 1)
        indexedOffsetData.AddNestedIndexedOffsetData(iod)

    return indexedOffsetData


iod = CreateIndexedOffsetDataset()

@benchmarkUtil.benchmark
def FlattenIndexedOffsetData():
    iod.Flatten()


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    benchmarkUtil.RunRegisteredBenchmarks('nestedIndexOffsetData_benchmark.log')
