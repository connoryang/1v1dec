#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\textImporting\importMultibuy.py
from collections import defaultdict
from evetypes import TypeNotFoundException
import evetypes
from textImporting import GetLines, StripImportantSymbol
QTY_NOT_FOUND = -1

class ImportMultibuy(object):

    def __init__(self, decimalSymbol, digitSymbol):
        self.decimalSymbol = decimalSymbol
        self.digitSymbol = digitSymbol

    def GetTypesAndQty(self, text):
        if not text:
            return ({}, [''])
        lines = GetLines(text)
        foundTypeIDs = defaultdict(int)
        failedLines = []
        for eachLine in lines:
            typeID, qty = self.ParseLine(eachLine)
            if typeID:
                foundTypeIDs[typeID] += qty
            else:
                failedLines.append(eachLine)

        return (foundTypeIDs, failedLines)

    def ParseLine(self, line):
        typeID = None
        foundTypeName = ''
        line = StripImportantSymbol(line)
        allParts = line.lower().split()
        qty = self._FindQty(allParts)
        if qty != QTY_NOT_FOUND:
            if len(allParts) < 1:
                return
            parts = allParts[1:]
            typeID, foundTypeName = FindTypeID(parts)
        if typeID is None:
            typeID, foundTypeName = FindTypeID(allParts)
            qty = QTY_NOT_FOUND
        if typeID and qty == QTY_NOT_FOUND:
            restOfLine = line.lower().replace(foundTypeName, '', 1).strip()
            parts = restOfLine.split()
            qty = self._FindQty(parts)
        if qty == QTY_NOT_FOUND:
            qty = 1
        return (typeID, qty)

    def _FindQty(self, parts):
        try:
            part = parts[0]
            part = part.strip('x')
            part = part.replace(self.digitSymbol, '')
            if self.decimalSymbol in part:
                part = part.replace(self.decimalSymbol, '.')
                part = float(part)
            qty = int(part)
        except (KeyError,
         TypeError,
         IndexError,
         ValueError):
            qty = QTY_NOT_FOUND

        return qty


def FindTypeID(parts):
    numParts = len(parts)
    for x in xrange(numParts, 0, -1):
        potentialName = ' '.join(parts[:x])
        try:
            typeID = evetypes.GetTypeIDByName(potentialName)
            return (typeID, potentialName)
        except TypeNotFoundException:
            continue

    return (None, None)
