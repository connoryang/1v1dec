#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fsd\diffMerge\findConflicts.py
from diffObjects import AreEqual
from sharedFunctions import IsPrimitive
from sharedFunctions import ListsAreOrderedTheSameWay
from sharedFunctions import ListIsLikelyToBeVector

def FindConflicts(base, mine, theirs):
    conflictLocations = []
    for conflictLocation in _GetConflictLocations(base, mine, theirs, []):
        conflictLocations.append(conflictLocation)

    return conflictLocations


def _GetConflictLocations(base, mine, theirs, pathList):
    if type(mine) == type(theirs) or IsPrimitive(mine) and IsPrimitive(theirs):
        for conflict in forwardTypeToCorrectFunction[type(mine).__name__](base, mine, theirs, pathList):
            yield conflict

    else:
        yield pathList


def _YieldLocationIfPrimitiveConflict(base, mine, theirs, pathList):
    if mine != theirs:
        if not AreEqual(base, mine) and not AreEqual(base, theirs):
            yield pathList


def _YieldLocationIfDictConflict(base, mine, theirs, pathList):
    conflictFinder = DictConflictFinder(base, mine, theirs, pathList)
    for conflict in conflictFinder.FindDictConflicts():
        yield conflict


def _YieldLocationIfListConflict(base, mine, theirs, pathList):
    if not AreEqual(mine, theirs):
        if not ListsAreOrderedTheSameWay(mine, theirs):
            if ListIsLikelyToBeVector(mine) or ListIsLikelyToBeVector(theirs):
                yield pathList


forwardTypeToCorrectFunction = {'int': _YieldLocationIfPrimitiveConflict,
 'bool': _YieldLocationIfPrimitiveConflict,
 'float': _YieldLocationIfPrimitiveConflict,
 'str': _YieldLocationIfPrimitiveConflict,
 'dict': _YieldLocationIfDictConflict,
 'list': _YieldLocationIfListConflict,
 'tuple': _YieldLocationIfListConflict,
 'unicode': _YieldLocationIfPrimitiveConflict}

class DictConflictFinder(object):

    def __init__(self, base, mine, theirs, pathList):
        self.base = base
        self.mine = mine
        self.theirs = theirs
        self.baseKeys = set(base.keys())
        self.myKeys = set(mine.keys())
        self.theirKeys = set(theirs.keys())
        self.pathList = pathList

    def _GetConflictLocationsOfDictKeysSharedBetweenBaseMineAndTheirs(self):
        commonKeys = self.baseKeys.intersection(self.myKeys, self.theirKeys)
        for key in commonKeys:
            for path in _GetConflictLocations(self.base[key], self.mine[key], self.theirs[key], self.pathList + [key]):
                yield path

    def _GetConflictLocationsOfDictKeysSharedBetweenMineAndTheirs(self):
        mineAndTheirKeys = self.myKeys.intersection(self.theirKeys).difference(self.baseKeys)
        for key in mineAndTheirKeys:
            for path in _GetConflictLocations({}, self.mine[key], self.theirs[key], self.pathList + [key]):
                yield path

    def _GetConflictLocationOfDictKeysChangedInMineAndRemovedFromTheirs(self):
        baseAndMineKeys = self.baseKeys.intersection(self.myKeys.difference(self.theirKeys))
        for key in baseAndMineKeys:
            if not AreEqual(self.base[key], self.mine[key]):
                yield self.pathList + [key]

    def _GetConflictLocationOfDictKeysChangedInTheirsAndRemovedFromMine(self):
        baseAndTheirKeys = self.baseKeys.intersection(self.theirKeys.difference(self.myKeys))
        for key in baseAndTheirKeys:
            if not AreEqual(self.base[key], self.theirs[key]):
                yield self.pathList + [key]

    def FindDictConflicts(self):
        for conflictLocation in self._GetConflictLocationsOfDictKeysSharedBetweenBaseMineAndTheirs():
            yield conflictLocation

        for conflictLocation in self._GetConflictLocationsOfDictKeysSharedBetweenMineAndTheirs():
            yield conflictLocation

        for conflictLocation in self._GetConflictLocationOfDictKeysChangedInMineAndRemovedFromTheirs():
            yield conflictLocation

        for conflictLocation in self._GetConflictLocationOfDictKeysChangedInTheirsAndRemovedFromMine():
            yield conflictLocation
