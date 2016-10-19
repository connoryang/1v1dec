#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\reprocessing\ui\outputItemAdder.py
from collections import defaultdict
import itertools
import inventorycommon.typeHelpers
from itertoolsext import Bundle
from reprocessing.util import CanBeReprocessed
import evetypes

class OutputItemAdder(object):

    def __init__(self, materialFetcher, outputContainer, itemCreator, grouper):
        self.materialFetcher = materialFetcher
        self.outputContainer = outputContainer
        self.itemCreator = itemCreator
        self.grouper = grouper
        self.items = {}
        self.groups = set()

    def UpdateItems(self):
        items = self._GetContainerInfo()
        self.outputContainer.ShowItems()
        self._RemoveContainers(items)
        groups = {self.grouper.GetGroupID(item) for item in items.itervalues()}
        self._RemoveGroups(groups)
        itemsToAdd, itemsToUpdate = self._GetItemsToAddAndUpdate(items)
        self._AddGroups(groups)
        self._AddContainers(itemsToAdd)
        self._UpdateContainers(itemsToUpdate)
        self._UpdateItemInfo(items)
        self.items = {i.typeID:i for i in items.itervalues()}
        self.groups = groups

    def _RemoveContainers(self, items):
        typeIDsToAdd = {i.typeID for i in items.itervalues()}
        for typeID, item in self.items.iteritems():
            if typeID not in typeIDsToAdd:
                self.outputContainer.RemoveItem(self.grouper.GetGroupID(item), typeID)

    def _AddContainers(self, itemsToAdd):
        containersToAdd = defaultdict(list)
        for item in itemsToAdd:
            containerInfo = GetAddParams(item, self.itemCreator.CreateOutputItems)
            containersToAdd[self.grouper.GetGroupID(item)].append(containerInfo)

        self.outputContainer.AddItems(containersToAdd)

    def _RemoveGroups(self, groups):
        for group in self.groups.difference(groups):
            self.outputContainer.RemoveGroup(group)

    def _AddGroups(self, groupIDs):
        groupIDsToAdd = groupIDs.difference(self.groups)
        if groupIDsToAdd:
            self.outputContainer.AddGroups([ (groupID, self.grouper.GetGroupName(groupID)) for groupID in groupIDsToAdd ])
        return groupIDs

    def _UpdateContainers(self, itemsToUpdate):
        for item in itemsToUpdate:
            self.outputContainer.UpdateInfo(self.grouper.GetGroupID(item), *GetUpdateParams(item))

    def _GetItemsToAddAndUpdate(self, items):
        itemsToUpdate = []
        itemsToAdd = []
        for item in items.itervalues():
            if item.typeID in self.items:
                itemsToUpdate.append(item)
            else:
                itemsToAdd.append(item)

        return (itemsToAdd, itemsToUpdate)

    def _GetContainerInfo(self):
        containerInfo = defaultdict(lambda : Bundle(typeID=None, fromTypeInfo=defaultdict(float), fromItemIDs=[], client=0, unrecoverable=0, iskCost=0.0))
        for material in self.materialFetcher.GetMaterials():
            ci = containerInfo[material.typeID]
            ci.typeID = material.typeID
            ci.fromItemIDs.append(material.fromItemID)
            ci.fromTypeInfo[material.fromTypeID] = material.client + material.unrecoverable
            ci.client += material.client
            ci.unrecoverable += material.unrecoverable
            ci.iskCost += material.iskCost

        return containerInfo

    def _GetAveragePrice(self, typeID):
        price = inventorycommon.typeHelpers.GetAveragePrice(typeID)
        if price is None:
            return 0.0
        return price

    def _UpdateItemInfo(self, items):
        numItems = len(items)
        price = sum((self._GetAveragePrice(typeID) * ci.client for typeID, ci in itertools.chain(items.iteritems())))
        volume = sum((evetypes.GetVolume(typeID) * ci.client for typeID, ci in items.iteritems()))
        self.outputContainer.UpdateItemInfo(price, numItems, volume)

    def GetItems(self):
        return self.items

    def GetTotalIskCost(self):
        items = self._GetContainerInfo()
        if not items:
            return 0.0
        return sum((i.iskCost for i in items.itervalues()))


def GetAddParams(item, createOutputItems):
    return (item.typeID, createOutputItems(item.typeID, (item.typeID,
      item.fromItemIDs,
      item.fromTypeInfo,
      (item.client, item.iskCost, item.unrecoverable),
      CanBeReprocessed(item.typeID))))


def GetUpdateParams(item):
    return (item.typeID,
     (item.client, item.iskCost, item.unrecoverable),
     item.fromItemIDs,
     item.fromTypeInfo)


class MaterialFetcher(object):

    def __init__(self, quotes):
        self.quotes = quotes

    def IterQuotes(self):
        return self.quotes.GetRawQuotes().iteritems()

    def GetMaterials(self):
        ret = []
        for itemID, item in self.IterQuotes():
            for r in item.recoverables:
                ret.append(Bundle(typeID=r.typeID, fromTypeID=item.typeID, fromItemID=itemID, client=r.client, iskCost=r.iskCost, unrecoverable=r.unrecoverable))

        return ret
