#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fsd\mapReduce\__init__.py
import os
import sys
import logging
import traceback
import time
import jobGenerator
import itertools
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

def AbsJoin(*args):
    return os.path.abspath(os.path.join(*args))


class RemoteProcessException(Exception):
    pass


class benchmark(object):

    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, ty, val, tb):
        end = time.time()
        log.info('%s : %0.3f seconds' % (self.name, end - self.start))
        return False


def GetSimpleTaskGenerator(walker, chunkSize, directoryFiles, include, exclude, mapReduceFinalizeFunctions):
    taskID = 0
    for chunk in ChunkIterable(jobGenerator.GetAllMatchingFiles(walker, directoryFiles, include, exclude), chunkSize):
        taskCount = 0
        task = RemoteProcessTask(taskID, walker)
        taskID += 1
        for filePath, relativePath, directoryPathStackForFile in chunk:
            validMapReduceOperations = [ job.GetValidMapReduceOperations(relativePath) for job in mapReduceFinalizeFunctions ]
            count = sum(map(len, validMapReduceOperations))
            taskCount += count
            if count:
                task.AddFileToTask(relativePath, directoryPathStackForFile, validMapReduceOperations)

        yield task


def GetSubDirectoryGroupedTaskGenerator(walker, subDirectoryGroupingDepth, directoryFiles, include, exclude, mapReduceFinalizeFunctions):
    taskID = 0
    for fileGroupSet in jobGenerator.GetAllMatchingFilesGroupedBySubdirectoryDepth(walker, directoryFiles, include, exclude, subDirectoryGroupingDepth):
        task = RemoteProcessTask(taskID, walker)
        taskID += 1
        totalCount = 0
        for filePath, relativePath, directoryPathStackForFile in fileGroupSet:
            validMapReduceOperations = [ job.GetValidMapReduceOperations(relativePath) for job in mapReduceFinalizeFunctions ]
            count = sum(map(len, validMapReduceOperations))
            if count:
                log.debug('Adding %s to task', relativePath)
                task.AddFileToTask(relativePath, directoryPathStackForFile, validMapReduceOperations)
                totalCount += count

        if totalCount:
            log.info('Created directory grouped task with %i files', len(task.fileTasks))
            yield task


def ChunkIterable(iterable, partitionSize):
    chunk = []
    for i in iterable:
        chunk.append(i)
        if len(chunk) == partitionSize:
            yield chunk
            chunk = []

    if len(chunk):
        yield chunk


def MapReduceMany(walker, directoryFiles, include, exclude, mapReduceFinalizeFunctions, pool, subDirectoryGroupingDepth = None, filesPerBatchWhenNotGrouped = 20):
    results = {}
    outputFiles = {}
    jobNames = set()
    with benchmark('FSD Map Reduce'):
        results = {}
        for job in mapReduceFinalizeFunctions:
            if job.name in jobNames:
                raise ValueError('Job with name %s was duplicated in job list!' % job.name)
            else:
                jobNames.add(job.name)
            if job.HasReduceFunction():
                results[job.name] = None
            else:
                results[job.name] = []

        if subDirectoryGroupingDepth is None:
            taskIterator = GetSimpleTaskGenerator(walker, filesPerBatchWhenNotGrouped, directoryFiles, include, exclude, mapReduceFinalizeFunctions)
        else:
            taskIterator = GetSubDirectoryGroupedTaskGenerator(walker, subDirectoryGroupingDepth, directoryFiles, include, exclude, mapReduceFinalizeFunctions)
        try:
            with benchmark('FSD Map Dispatch'):
                for r in pool.imap_unordered(PerformMapOperationsForAllJobsOnFileInOtherProcess, taskIterator, 1):
                    for i, job in enumerate(mapReduceFinalizeFunctions):
                        jobName = job.name
                        try:
                            if jobName in r:
                                if job.StoreOutputInTemporaryFiles():
                                    if job.name in outputFiles:
                                        outputFiles[jobName].append(r[jobName])
                                    else:
                                        outputFiles[jobName] = [r[jobName]]
                                else:
                                    results[jobName] = job.Reduce(r[jobName], results[jobName])
                        except:
                            log.critical('Error when reducing %s', jobName)
                            raise

        except RemoteProcessException as e:
            log.error('Exception occured on worker process:\n %s' % str(e))
            raise Exception('Terminating due to remote exception:\n' + str(e))

        for i, job in enumerate(mapReduceFinalizeFunctions):
            jobName = job.name
            with benchmark('Finalize %s' % jobName):
                if job.StoreOutputInTemporaryFiles() and jobName in outputFiles:
                    results[jobName] = MergeOutputFromIntermediateFiles(pool, walker, outputFiles[jobName], job)
                else:
                    results[jobName] = job.Finalize(walker.GetRoot(), results[jobName])

    return results


def MergeIntermediateFilesOnRemoteProcess(args):
    walker, jobName, uniqueID, mergeFunction, reduceFunction, chunkedfileNames = args
    outputFileName = '%s/Merge-%i.tmp' % (jobName, uniqueID)
    outFile = walker.GetTemporaryFileForWriting(outputFileName, 'rb')
    mergeFunction(outFile, reduceFunction, [ walker.OpenTemporaryFileForReading(f) for f in chunkedfileNames ])
    walker.CloseTemporaryWriteFiles()
    return outputFileName


MAX_OPEN_FILES = 256
FILE_MERGE_CHUNK_SIZE = 10

def MergeOutputFromIntermediateFiles(pool, walker, mergeFiles, job):
    intermediateFiles = mergeFiles
    if len(intermediateFiles) < MAX_OPEN_FILES:
        files = [ walker.OpenTemporaryFileForReading(f) for f in intermediateFiles ]
        return job.ReduceAndFinalizeFromTemporaryFiles(files)
    else:
        mergeFunction = job.GetIncrementalFileMergeFunction()
        uniqueCounter = itertools.count()
        repeated_walker = itertools.repeat(walker)
        repeated_job_name = itertools.repeat(job.name)
        repeated_merge_fn = itertools.repeat(mergeFunction)
        repeated_reduce_fn = itertools.repeat(job.reduceFunction)
        while len(intermediateFiles) >= MAX_OPEN_FILES:
            mergeBlocks = ChunkIterable(intermediateFiles, FILE_MERGE_CHUNK_SIZE)
            newIntermediateFiles = []
            mapArguments = itertools.izip(repeated_walker, repeated_job_name, uniqueCounter, repeated_merge_fn, repeated_reduce_fn, mergeBlocks)
            for resultFile in pool.imap_unordered(MergeIntermediateFilesOnRemoteProcess, mapArguments, 1):
                newIntermediateFiles.append(resultFile)

            intermediateFiles = newIntermediateFiles

        files = [ walker.OpenTemporaryFileForReading(f) for f in intermediateFiles ]
        return job.ReduceAndFinalizeFromTemporaryFiles(files)


class RemoteProcessTask(object):

    def __init__(self, uniqueTaskID, walker):
        self.uniqueTaskID = uniqueTaskID
        self.walker = walker
        self.fileTasks = []

    def AddFileToTask(self, relativePath, directoryFilePaths, jobs):
        self.fileTasks.append([relativePath, directoryFilePaths, jobs])

    def Execute(self):
        resultsByJob = {}
        listMergeFunctionsByJob = {}
        reduceByJob = {}
        directoryFiles = {}
        persistFunctionsByJob = {}
        for relativePath, directoryFilePaths, jobs in self.fileTasks:
            for f in directoryFilePaths:
                if f not in directoryFiles:
                    log.info('Opening directory file %s', f)
                    contents = self.walker.GetFileContents(AbsJoin(self.walker.GetRoot(), f))
                    directoryFiles[f] = contents

            if len(directoryFilePaths) > 0:
                curDir = directoryFilePaths[-1]
                if not self.walker.IsFolderIncluded(directoryFiles[curDir]):
                    continue
            path = AbsJoin(self.walker.GetRoot(), relativePath)
            with benchmark('File Open and Read: %s' % path):
                data = self.walker.GetFileContents(path)
            for jobIndex, job in enumerate(jobs):
                for jobName, mapName, mapFunction, mapKwargs, reduceFunction, isGeneratorFunction, listMergeFunction, persistFunction in job:
                    if reduceFunction is not None:
                        reduceByJob[jobName] = reduceFunction
                    if jobName not in resultsByJob:
                        resultsByJob[jobName] = []
                    if persistFunction is not None:
                        persistFunctionsByJob[jobName] = persistFunction
                    if listMergeFunction is not None:
                        listMergeFunctionsByJob[jobName] = listMergeFunction
                    stack = [ directoryFiles[i] for i in directoryFilePaths ]
                    with benchmark('Map: %s' % mapName):
                        try:
                            if mapKwargs is None:
                                mapKwargs = {}
                            functionResult = mapFunction(self.walker.GetRoot(), relativePath, stack, data, **mapKwargs)
                        except Exception as e:
                            raise RemoteProcessException('Exception while running map function "%s" on file: %s \n%s' % (mapName, path, traceback.format_exc()))

                    if isGeneratorFunction:
                        try:
                            allResults = [ r for r in functionResult ]
                        except Exception as e:
                            raise RemoteProcessException('Exception while running map function "%s" on file: %s \n%s' % (mapName, path, traceback.format_exc()))

                        resultsByJob[jobName].extend(allResults)
                    else:
                        resultsByJob[jobName].append(functionResult)

        for jobName in resultsByJob.keys():
            if jobName in persistFunctionsByJob:
                temporaryFileName = '%s/%i.tmp' % (jobName, self.uniqueTaskID)
                log.info('Writing results to intermediate file: %s', temporaryFileName)
                f = self.walker.GetTemporaryFileForWriting(temporaryFileName, 'wb')
                listReduceFunction = listMergeFunctionsByJob[jobName]
                if jobName in reduceByJob:
                    iterableResults = listReduceFunction([ i[1] for i in resultsByJob[jobName] ])
                    reducibleResults = [ i[0] for i in resultsByJob[jobName] ]
                    reduceFunction = reduceByJob[jobName]
                    reducedResults = reduceFunction(None, reducibleResults)
                    persistFunctionsByJob[jobName](f, reducedResults, len(iterableResults), iterableResults)
                else:
                    iterableResults = listReduceFunction(resultsByJob[jobName])
                    persistFunctionsByJob[jobName](f, None, len(iterableResults), iterableResults)
                resultsByJob[jobName] = temporaryFileName
            elif jobName in reduceByJob:
                resultsByJob[jobName] = [reduceByJob[jobName](None, resultsByJob[jobName])]

        if len(persistFunctionsByJob):
            self.walker.CloseTemporaryWriteFiles()
        return resultsByJob


def PerformMapOperationsForAllJobsOnFileInOtherProcess(a):
    return a.Execute()
