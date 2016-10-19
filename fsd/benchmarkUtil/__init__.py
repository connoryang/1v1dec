#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fsd\benchmarkUtil\__init__.py
import datetime
import time
import logging
import os
import cPickle
_log = logging.getLogger(__name__)
_registered_benchmarks = []

def benchmark(fn):
    _registered_benchmarks.append(fn)
    return fn


def RunBenchmarks(benchmarks, outputFile, resultTolerance = 0.02):
    pickleFile = outputFile.replace('.log', '.pickle')
    if os.path.exists(pickleFile):
        with open(pickleFile, 'rb') as f:
            fastestTimes = cPickle.load(f)
    else:
        fastestTimes = {}
    with open(outputFile, 'a') as f:
        s = 'Benchmark @%s\n' % datetime.datetime.now()
        _log.info(s.strip())
        f.write(s)
        sortedBenchmarks = sorted(benchmarks, key=lambda i: i.__name__)
        for benchmark in sortedBenchmarks:
            benchmarkName = benchmark.__name__
            start = time.clock()
            benchmark()
            timeForBenchmark = time.clock() - start
            if benchmarkName in fastestTimes:
                fastestTime, fastestTimeOccurance = fastestTimes[benchmarkName]
                proportionalDifference = (timeForBenchmark - fastestTime) / fastestTime
                if abs(proportionalDifference) > resultTolerance:
                    s = '\t%s: %s %s, was %s (%s)\n' % (benchmarkName,
                     '(FASTER)' if fastestTime > timeForBenchmark else '(SLOWER)',
                     timeForBenchmark,
                     fastestTime,
                     timeForBenchmark - fastestTime)
                else:
                    s = '\t%s: %s\n' % (benchmarkName, timeForBenchmark)
                if fastestTime > timeForBenchmark:
                    fastestTimes[benchmarkName] = (timeForBenchmark, '')
            else:
                s = '\t%s: %s\n' % (benchmarkName, timeForBenchmark)
                fastestTimes[benchmarkName] = (timeForBenchmark, '')
            _log.info(s.strip())
            f.write(s)

    with open(pickleFile, 'wb') as f:
        cPickle.dump(fastestTimes, f)


def RunRegisteredBenchmarks(outputFile):
    RunBenchmarks(_registered_benchmarks, outputFile)
