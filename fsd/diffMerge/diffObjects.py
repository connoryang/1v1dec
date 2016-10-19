#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fsd\diffMerge\diffObjects.py
from sharedFunctions import IsPrimitive

def AreEqual(mine, theirs):
    if type(mine) == type(theirs):
        return forwardTypeToCorrectFunction[type(mine).__name__](mine, theirs)
    elif IsPrimitive(mine) and IsPrimitive(theirs):
        return _PrimitivesAreEqual(mine, theirs)
    else:
        return False


def _PrimitivesAreEqual(mine, theirs):
    return mine == theirs


def _ListsAreEqual(mine, theirs):
    if len(mine) != len(theirs):
        return False
    for itemMine, itemTheirs in zip(mine, theirs):
        if not AreEqual(itemMine, itemTheirs):
            return False

    return True


def _DictsHaveSameKeys(mine, theirs):
    keysInAButNotInB = set(mine.keys()).difference(set(theirs.keys()))
    return len(keysInAButNotInB) == 0


def _DictsHaveSameValues(mine, theirs):
    for key in mine.keys():
        if not AreEqual(mine[key], theirs[key]):
            return False

    return True


def _DictsAreEqual(mine, theirs):
    if _DictsHaveSameKeys(mine, theirs):
        if _DictsHaveSameValues(mine, theirs):
            return True
    return False


forwardTypeToCorrectFunction = {'int': _PrimitivesAreEqual,
 'str': _PrimitivesAreEqual,
 'float': _PrimitivesAreEqual,
 'bool': _PrimitivesAreEqual,
 'unicode': _PrimitivesAreEqual,
 'list': _ListsAreEqual,
 'dict': _DictsAreEqual,
 'tuple': _ListsAreEqual}
