#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fsd\diffMerge\frameworkInterface.py
from mergeObjects import PerformSafeMerge
from findConflicts import FindConflicts
from diffObjects import AreEqual
from sharedFunctions import ListsAreOrderedTheSameWay
from sharedFunctions import ListIsLikelyToBeVector

class FsdDiffMerger(object):

    def __init__(self, base, mine, theirs):
        self.base = base
        self.mine = mine
        self.theirs = theirs
        self.resultData = {}
        self.conflicts = []
        self.differences = {}
        self.differenceFinder = DifferenceFinder()

    def PerformSafeMerge(self):
        try:
            self.resultData = PerformSafeMerge(self.base, self.mine, self.theirs).next()
        except StopIteration:
            self.resultData = {}

    def GetResultData(self):
        return self.resultData

    def PerformConflictSearch(self):
        self.conflicts = FindConflicts(self.base, self.mine, self.theirs)

    def GetConflicts(self):
        return self.conflicts

    def SolveConflictUsingMine(self, conflictLocation):
        value = self.GetObjectAtLocation(self.mine, conflictLocation)
        self.InsertItemAtLocation(value, conflictLocation)

    def SolveConflictUsingTheirs(self, conflictLocation):
        value = self.GetObjectAtLocation(self.theirs, conflictLocation)
        self.InsertItemAtLocation(value, conflictLocation)

    def SolveConflictUsingBase(self, conflictLocation):
        value = self.GetObjectAtLocation(self.base, conflictLocation)
        self.InsertItemAtLocation(value, conflictLocation)

    def PerformDifferenceCheck(self, seeAddsInLists = False):
        self.differenceFinder.FindDifferences(self.base, self.mine, self.theirs, [], seeAddsInLists)

    def GetDifferences(self):
        return self.differenceFinder.GetSortedDifferences()

    def GetObjectAtLocation(self, source, location):
        for key in location:
            if source is not None:
                if type(source) is dict:
                    source = source.get(key, None)
                else:
                    source = source[key]

        return source

    def InsertItemAtLocation(self, item, location):
        InsertItemToDictionaryAtLocation(self.resultData, location, item)


def _ItemWasNotDeleted(item):
    return item is not None


def InsertItemToDictionaryAtLocation(d, keysToLocation, item):
    for key in keysToLocation[:-1]:
        d = d[key]

    lastKey = keysToLocation[-1]
    if _ItemWasNotDeleted(item):
        d[lastKey] = item
    else:
        d.pop(lastKey, None)


class DifferenceFinder(object):

    def __init__(self):
        self.differences = {'added': [],
         'changed': []}
        self.isSorted = False

    def _ItemsAreOfPrimitiveTypes(self, baseItem, myItem, theirItem):
        return type(baseItem) is not dict and type(myItem) is not dict and type(theirItem) is not dict

    def _FindDictDifferencesInSharedKeys(self, base, baseKeys, mine, myKeys, path, theirKeys, theirs):
        keysInAll = baseKeys.intersection(myKeys, theirKeys)
        for key in keysInAll:
            if self._ItemsAreOfPrimitiveTypes(base[key], mine[key], theirs[key]):
                if not AreEqual(base[key], mine[key]) and AreEqual(base[key], theirs[key]):
                    self.differences['changed'].append(path + [key])
                if not AreEqual(base[key], theirs[key]) and AreEqual(base[key], mine[key]):
                    self.differences['changed'].append(path + [key])
            self.FindDifferences(base[key], mine[key], theirs[key], path + [key])

    def _FindDictDifferencesInKeysOnlyInMineAndTheirs(self, baseKeys, myKeys, path, theirKeys):
        keysInMineAndTheirs = myKeys.intersection(theirKeys).difference(baseKeys)
        for key in keysInMineAndTheirs:
            self.differences['added'].append(path + [key])

    def _FindDictDifferencesInKeysOnlyInMine(self, baseKeys, myKeys, path, theirKeys):
        keysOnlyInMine = myKeys.difference(baseKeys, theirKeys)
        for key in keysOnlyInMine:
            self.differences['added'].append(path + [key])

    def _FindDictDifferencesInKeysOnlyInTheirs(self, baseKeys, myKeys, path, theirKeys):
        keysOnlyInTheirs = theirKeys.difference(baseKeys, myKeys)
        for key in keysOnlyInTheirs:
            self.differences['added'].append(path + [key])

    def _FindDifferencesInLists(self, base, mine, theirs, path, seeAddsInLists):
        if not AreEqual(mine, theirs):
            if not AreEqual(base, mine) and AreEqual(base, theirs):
                self.differences['changed'].append(path)
            elif not AreEqual(base, theirs) and AreEqual(base, mine):
                self.differences['changed'].append(path)
            elif not ListIsLikelyToBeVector(mine) and not ListIsLikelyToBeVector(theirs):
                if ListsAreOrderedTheSameWay(mine, theirs):
                    self.differences['changed'].append(path)
                    if seeAddsInLists:
                        for index, item in enumerate(mine):
                            if item not in theirs:
                                self.differences['added'].append(path + [index])

    def FindDifferences(self, base, mine, theirs, path, seeAddsInLists = False):
        if type(base) is dict and type(mine) is dict and type(theirs) is dict:
            baseKeys = set(base.keys())
            myKeys = set(mine.keys())
            theirKeys = set(theirs.keys())
            self._FindDictDifferencesInSharedKeys(base, baseKeys, mine, myKeys, path, theirKeys, theirs)
            self._FindDictDifferencesInKeysOnlyInMineAndTheirs(baseKeys, myKeys, path, theirKeys)
            self._FindDictDifferencesInKeysOnlyInMine(baseKeys, myKeys, path, theirKeys)
            self._FindDictDifferencesInKeysOnlyInTheirs(baseKeys, myKeys, path, theirKeys)
        elif type(mine) is list and type(theirs) is list:
            self._FindDifferencesInLists(base, mine, theirs, path, seeAddsInLists)

    def GetSortedDifferences(self):
        if not self.isSorted:
            self.differences['added'].sort()
            self.differences['changed'].sort()
            self.isSorted = True
        return self.differences
