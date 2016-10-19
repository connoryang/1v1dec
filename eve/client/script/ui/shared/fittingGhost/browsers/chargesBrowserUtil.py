#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\browsers\chargesBrowserUtil.py
import evetypes
import uix
from carbonui.primitives.line import Line
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.ui.control import entries as listentry
from utillib import KeyVal
from eve.client.script.ui.control.entries import Line as ListentryLine
import carbonui.const as uiconst

class ChargeBrowserListProvider(object):

    def __init__(self, dblClickFunc, onDropDataFunc, reloadFunc):
        self.dblClickFunc = dblClickFunc
        self.onDropDataFunc = onDropDataFunc
        self.reloadFunc = reloadFunc

    def GetChargesScrollList(self, moduleTypeID, chargeTypeIDs):
        godma = sm.GetService('godma')
        scrolllist = []
        factionChargeIDs = set()
        otherChargeIDs = set()
        for eachTypeID in chargeTypeIDs:
            metaGroup = godma.GetTypeAttribute(eachTypeID, const.attributeMetaGroupID)
            if metaGroup == const.metaGroupFaction:
                factionChargeIDs.add(eachTypeID)
            else:
                otherChargeIDs.add(eachTypeID)

        if chargeTypeIDs:
            label = 'Favorites'
            data = {'GetSubContent': self._GetFavoritesContent,
             'label': label,
             'id': ('ammobrowser', 'favorites'),
             'showlen': 0,
             'chargeTypeIDs': chargeTypeIDs,
             'sublevel': 0,
             'showicon': 'hide',
             'state': 'locked',
             'BlockOpenWindow': True,
             'DropData': self._DropOnFavorites,
             'moduleTypeID': moduleTypeID}
            scrolllist.append(listentry.Get('Group', data=data))
            scrolllist.append(listentry.Get(data=KeyVal(height=6), decoClass=HorizontalLine))
        scrolllist += self._GetScrollListFromTypeList(moduleTypeID, otherChargeIDs)
        if factionChargeIDs:
            label = cfg.invmetagroups.Get(const.metaGroupFaction).metaGroupName
            data = {'GetSubContent': self._GetAmmoSubContent,
             'label': label,
             'id': ('ammobrowser', 'factionChargeIDs'),
             'showlen': 0,
             'chargeTypeIDs': factionChargeIDs,
             'sublevel': 0,
             'showicon': uix.GetTechLevelIconID(const.metaGroupFaction),
             'state': 'locked',
             'BlockOpenWindow': True,
             'moduleTypeID': moduleTypeID}
            scrolllist.append(listentry.Get('Group', data=data))
        return scrolllist

    def _GetFavoritesContent(self, nodedata, *args):
        moduleTypeID = nodedata.moduleTypeID
        typeIDs = nodedata.chargeTypeIDs
        favoriteChargeIDs = set()
        allFavorites = settings.user.ui.Get('fitting_ammowbrowserFavorites', [])
        for eachTypeID in typeIDs:
            if eachTypeID in allFavorites:
                favoriteChargeIDs.add(eachTypeID)

        return self._GetScrollListFromTypeList(moduleTypeID, favoriteChargeIDs, sublevel=1, isFavorite=True)

    def _GetAmmoSubContent(self, nodedata, *args):
        moduleTypeID = nodedata.moduleTypeID
        typeIDs = nodedata.chargeTypeIDs
        return self._GetScrollListFromTypeList(moduleTypeID, typeIDs, sublevel=1)

    def _GetScrollListFromTypeList(self, moduleTypeID, chargeTypeIDs, sublevel = 0, isFavorite = False):
        scrolllist = []
        godma = sm.GetService('godma')
        for eachTypeID in chargeTypeIDs:
            label = evetypes.GetName(eachTypeID)
            data = KeyVal(label=label, typeID=eachTypeID, itemID=None, getIcon=1, OnDropData=self.onDropDataFunc, OnDblClick=(self.dblClickFunc, moduleTypeID, eachTypeID), sublevel=sublevel, GetMenu=self._GetChargeMenu, isFavorite=isFavorite, ignoreRightClick=isFavorite)
            techLevel = godma.GetTypeAttribute(eachTypeID, const.attributeTechLevel)
            scrolllist.append(((techLevel, label), listentry.Get('Item', data=data)))

        scrolllist = SortListOfTuples(scrolllist)
        return scrolllist

    def _GetChargeMenu(self, entry, *args):
        node = entry.sr.node
        typeID = entry.typeID
        selectedNodes = node.scroll.GetSelectedNodes(node)
        removableTypeIDs = set()
        for eachNode in selectedNodes:
            if node.get('isFavorite', False):
                removableTypeIDs.add(eachNode.typeID)

        m = []
        if removableTypeIDs:
            m += [('Remove from favorite', self._RemoveFromFavorite, (removableTypeIDs,))]
        if len(selectedNodes) == 1:
            m += sm.GetService('menu').GetMenuFormItemIDTypeID(None, typeID, ignoreMarketDetails=0)
        return m

    def _RemoveFromFavorite(self, removableTypeIDs):
        allFavoritesSet = settings.user.ui.Get('fitting_ammowbrowserFavorites', [])
        for eachTypeID in removableTypeIDs:
            allFavoritesSet.discard(eachTypeID)

        settings.user.ui.Set('fitting_ammowbrowserFavorites', allFavoritesSet)
        self.reloadFunc()

    def _DropOnFavorites(self, dragObj, nodes):
        allFavoritesSet = settings.user.ui.Get('fitting_ammowbrowserFavorites', set())
        for eachNode in nodes:
            try:
                if not IsCharge(eachNode.typeID):
                    continue
                allFavoritesSet.add(eachNode.typeID)
            except:
                continue

        settings.user.ui.Set('fitting_ammowbrowserFavorites', allFavoritesSet)
        self.reloadFunc()


def IsCharge(typeID):
    return evetypes.GetCategoryID(typeID) == const.categoryCharge


class HorizontalLine(ListentryLine):

    def ApplyAttributes(self, attributes):
        ListentryLine.ApplyAttributes(self, attributes)
        Line(parent=self, align=uiconst.TOTOP, color=(1, 1, 1, 0.07))
