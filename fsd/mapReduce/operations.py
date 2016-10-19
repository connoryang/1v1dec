#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fsd\mapReduce\operations.py
import logging
import inspect
import heapq
from iterativePickle import IterativePickleWithHeaderObject
import cPickle
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

class MapOperation(object):

    def __init__(self, name, mapFunction, pathConditional = None, mapKwargs = None):
        self.name = name
        self.conditional = pathConditional
        self.mapFunction = mapFunction
        self.isGenerator = inspect.isgeneratorfunction(mapFunction)
        self.mapKwargs = mapKwargs
        if mapKwargs:
            cPickle.dumps(mapKwargs)

    def IsValidOnPath(self, path):
        if self.conditional is None:
            return True
        elif self.conditional.Matches(path):
            log.debug('Running Map %s on %s (matches conditional)', self.name, path)
            return True
        else:
            log.debug('Skipping Map %s on %s due to path conditional', self.name, path)
            return False


class MapReduceFinalizeJob(object):

    def __init__(self, name, mapOperations, pathConditional = None, reduceFunction = None, finalizeFunction = None):
        self.name = name
        self.conditional = pathConditional
        self.mapOperations = mapOperations
        self.reduceFunction = reduceFunction
        self.finalizeFunction = finalizeFunction

    def GetValidMapReduceOperations(self, path):
        if self.conditional is not None and not self.conditional.Matches(path):
            log.debug('Skipping job %s on %s due to job path conditional', self.name, path)
            return []
        validMapOperations = []
        for mapOperation in self.mapOperations:
            if mapOperation.IsValidOnPath(path):
                log.debug('Map operation %s pending on %s', mapOperation.name, path)
                validMapOperations.append(self.GetOperationInfo(mapOperation))

        return validMapOperations

    def GetOperationInfo(self, mapOperation):
        return (self.name,
         mapOperation.name,
         mapOperation.mapFunction,
         mapOperation.mapKwargs,
         self.reduceFunction,
         mapOperation.isGenerator,
         None,
         None)

    def HasReduceFunction(self):
        return self.reduceFunction is not None

    def StoreOutputInTemporaryFiles(self):
        return False

    def Reduce(self, data, existingResult):
        if self.reduceFunction is not None:
            return self.reduceFunction(existingResult, data)
        else:
            existingResult.extend(data)
            return existingResult

    def Finalize(self, rootPath, data):
        if self.finalizeFunction is None:
            return data
        else:
            return self.finalizeFunction(rootPath, data)


def SaveResultsToFileObject(fileobject, reducedSummary, count, sortedResults):
    IterativePickleWithHeaderObject.WriteIterableWithHeaderAndLengthAsIterativePickle(fileobject, reducedSummary, count, sortedResults)


def MergeSortedIntermediateFiles(outfile, reduceFunction, mergeFiles):
    files = [ IterativePickleWithHeaderObject(i) for i in mergeFiles ]
    totalCount = sum(map(len, files))
    if reduceFunction is not None:
        summariesForReducing = [ i.header for i in files ]
        reducedSummary = reduceFunction(None, summariesForReducing)
    else:
        reducedSummary = None
    IterativePickleWithHeaderObject.WriteIterableWithHeaderAndLengthAsIterativePickle(outfile, reducedSummary, totalCount, heapq.merge(*files))


class MapReduceSortedStreamJob(MapReduceFinalizeJob):

    def __init__(self, name, mapOperations, incrementalFinalizeFunction, pathConditional = None, reduceFunction = None):
        MapReduceFinalizeJob.__init__(self, name, mapOperations, pathConditional, reduceFunction=reduceFunction, finalizeFunction=None)
        self.incrementalFinalizeFunction = incrementalFinalizeFunction

    def GetOperationInfo(self, mapOperation):
        return (self.name,
         mapOperation.name,
         mapOperation.mapFunction,
         mapOperation.mapKwargs,
         self.reduceFunction,
         mapOperation.isGenerator,
         sorted,
         SaveResultsToFileObject)

    def StoreOutputInTemporaryFiles(self):
        return True

    def GetIncrementalFileMergeFunction(self):
        return MergeSortedIntermediateFiles

    def ReduceAndFinalizeFromTemporaryFiles(self, fileObjects):
        files = [ IterativePickleWithHeaderObject(i) for i in fileObjects ]
        totalCount = sum(map(len, files))
        if self.HasReduceFunction():
            summariesForReducing = [ i.header for i in files ]
            reducedSummary = self.reduceFunction(None, summariesForReducing)
            return self.incrementalFinalizeFunction(totalCount, reducedSummary, heapq.merge(*files))
        else:
            return self.incrementalFinalizeFunction(totalCount, None, heapq.merge(*files))
