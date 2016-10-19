#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\reprocessing\ui\quotes.py
from collections import defaultdict
import inventorycommon.const as invconst
from reprocessing.ui.efficiencyCalculator import CalculateTheoreticalEfficiency
import evetypes

class Quotes(object):

    def __init__(self, reprocessingSvc):
        self.reprocessingSvc = reprocessingSvc
        self.rawQuotes = {}
        self.stationEfficiency = None
        self.stationTax = None

    def GetQuotes(self, itemIDs, activeShipID):
        self.stationTax, self.stationEfficiency, self.rawQuotes = self.reprocessingSvc.GetReprocessingSvc().GetQuotes(itemIDs, activeShipID)
        return self._GetQuotes()

    def _GetQuotes(self):
        ret = defaultdict(list)
        for itemID, item in self.rawQuotes.iteritems():
            for r in item.recoverables:
                ret[itemID].append((r.typeID, r.client))

        return ret

    def GetRawQuotes(self):
        return self.rawQuotes

    def GetHint(self, itemID, typeID):
        reprocessingYieldHint = self._GetReprocessingYield(typeID)
        itemYieldHint = self.GetHintInfo(itemID)
        stationEfficiency = self.GetStationEfficiencyForType(typeID)
        return (typeID,
         reprocessingYieldHint,
         self.stationTax,
         itemYieldHint,
         stationEfficiency)

    def GetHintInfo(self, itemID):
        if itemID not in self.rawQuotes:
            return []
        rawQuote = self.rawQuotes[itemID]
        return [ (r.typeID, r.client) for r in rawQuote.recoverables ]

    def _GetReprocessingYield(self, typeID):
        efficiency = self.GetStationEfficiencyForType(typeID)
        return CalculateTheoreticalEfficiency([typeID], efficiency)

    def GetStationEfficiencyForType(self, typeID):
        return self.stationEfficiency.get(typeID, self.stationEfficiency[None])

    def GetClientMaterial(self, itemID):
        ret = {}
        try:
            recoverables = self.rawQuotes[itemID].recoverables
        except KeyError:
            return {}

        for r in recoverables:
            ret[r.typeID] = r.client

        return ret

    def GetOutputItemsForItemIDs(self, itemIDs):
        ret = []
        for itemID in itemIDs:
            if itemID in self.rawQuotes:
                rawQuote = self.rawQuotes[itemID]
                ret.extend(rawQuote.recoverables)

        return ret

    def GetOutputTypesForItemID(self, itemID):
        if itemID not in self.rawQuotes:
            return {}
        return {r.typeID:r.client for r in self.rawQuotes[itemID].recoverables}

    def RemoveItem(self, itemID):
        try:
            del self.rawQuotes[itemID]
        except KeyError:
            pass

        return self._GetQuotes()
