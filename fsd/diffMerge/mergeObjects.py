#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fsd\diffMerge\mergeObjects.py
from diffObjects import AreEqual
from sharedFunctions import IsPrimitive
from sharedFunctions import ListIsSortedAscending
from sharedFunctions import ListsAreOrderedTheSameWay
from sharedFunctions import ListIsLikelyToBeVector

def PerformSafeMerge(base, mine, theirs):
    if type(mine) == type(theirs):
        return forwardTypeToCorrectFunction[type(mine).__name__](base, mine, theirs)
    elif IsPrimitive(mine) and IsPrimitive(theirs):
        return _PrimitiveSafeMerge(base, mine, theirs)
    else:
        return {}


def _PrimitiveSafeMerge(base, mine, theirs):
    if mine == theirs:
        yield mine
    elif not AreEqual(base, mine) and AreEqual(base, theirs):
        yield mine
    elif not AreEqual(base, theirs) and AreEqual(base, mine):
        yield theirs
    else:
        yield base


def _DictSafeMerge(base, mine, theirs):
    yield DictSafeMerger(base, mine, theirs).DoSafeMerge()


def _JoinLists(mine, theirs):
    return sorted(list(set(mine + theirs)))


def _ListSafeMerge(base, mine, theirs):
    if AreEqual(mine, theirs):
        yield mine
    elif not AreEqual(base, mine) and AreEqual(base, theirs):
        yield mine
    elif not AreEqual(base, theirs) and AreEqual(base, mine):
        yield theirs
    elif ListIsLikelyToBeVector(mine) or ListIsLikelyToBeVector(theirs):
        yield base
    elif ListsAreOrderedTheSameWay(mine, theirs):
        result = _JoinLists(mine, theirs)
        if ListIsSortedAscending(mine):
            yield result
        else:
            yield [ x for x in reversed(result) ]


forwardTypeToCorrectFunction = {'int': _PrimitiveSafeMerge,
 'bool': _PrimitiveSafeMerge,
 'float': _PrimitiveSafeMerge,
 'str': _PrimitiveSafeMerge,
 'dict': _DictSafeMerge,
 'list': _ListSafeMerge,
 'tuple': _ListSafeMerge,
 'unicode': _PrimitiveSafeMerge}

class DictSafeMerger(object):

    def __init__(self, base, mine, theirs):
        self.base = base
        self.mine = mine
        self.theirs = theirs
        self.baseKeys = set(base.keys())
        self.myKeys = set(mine.keys())
        self.theirKeys = set(theirs.keys())

    def _SafeMergeKeysInBaseMineAndTheirs(self):
        commonKeys = self.baseKeys.intersection(self.myKeys, self.theirKeys)
        for key in commonKeys:
            value = PerformSafeMerge(self.base[key], self.mine[key], self.theirs[key])
            if value == {}:
                self.mergeResult[key] = {}
            else:
                self.mergeResult[key] = value.next()

    def _SafeMergeKeysOnlyInMineAndTheirs(self):
        mineAndTheirKeys = self.myKeys.intersection(self.theirKeys).difference(self.baseKeys)
        for key in mineAndTheirKeys:
            value = PerformSafeMerge({}, self.mine[key], self.theirs[key])
            if value == {}:
                self.mergeResult[key] = {}
            else:
                self.mergeResult[key] = value.next()

    def _SafeMergeKeysOnlyInMine(self):
        onlyMyKeys = self.myKeys.difference(self.theirKeys, self.baseKeys)
        for key in onlyMyKeys:
            self.mergeResult[key] = self.mine[key]

    def _SafeMergeKeysOnlyInTheirs(self):
        onlyTheirKeys = self.theirKeys.difference(self.myKeys, self.baseKeys)
        for key in onlyTheirKeys:
            self.mergeResult[key] = self.theirs[key]

    def _SafeMergeKeysChangedInMineAndRemovedFromTheirs(self):
        keysInMineAndBaseNotInTheirs = self.baseKeys.intersection(self.myKeys).difference(self.theirKeys)
        for key in keysInMineAndBaseNotInTheirs:
            if not AreEqual(self.base[key], self.mine[key]):
                self.mergeResult[key] = self.base[key]

    def _SafeMergeKeysChangedInTheirsAndRemovedFromMine(self):
        keysInTheirsAndBaseNotInMine = self.baseKeys.intersection(self.theirKeys).difference(self.myKeys)
        for key in keysInTheirsAndBaseNotInMine:
            if not AreEqual(self.base[key], self.theirs[key]):
                self.mergeResult[key] = self.base[key]

    def DoSafeMerge(self):
        self.mergeResult = {}
        self._SafeMergeKeysInBaseMineAndTheirs()
        self._SafeMergeKeysOnlyInMineAndTheirs()
        self._SafeMergeKeysOnlyInMine()
        self._SafeMergeKeysOnlyInTheirs()
        self._SafeMergeKeysChangedInMineAndRemovedFromTheirs()
        self._SafeMergeKeysChangedInTheirsAndRemovedFromMine()
        return self.mergeResult
