#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\browsers\fittingBrowser.py
from collections import defaultdict
import itertools
import uix
from carbon.common.script.sys.serviceConst import ROLE_WORLDMOD, ROLEMASK_ELEVATEDPLAYER
from carbonui import const as uiconst
from carbonui.control.menuLabel import MenuLabel
from carbonui.primitives.sprite import Sprite
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.control import entries as listentry
from eve.client.script.ui.control.buttons import ButtonIcon
from eve.client.script.ui.control.entries import Item
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.listgroup import ListGroup as Group
from carbonui.primitives.container import Container
import evetypes
from eve.client.script.ui.shared.fittingMgmtWindow import OpenOrLoadMultiFitWnd
from eve.client.script.ui.shared.traits import HasTraits, TraitsContainer
from eve.common.script.sys.eveCfg import IsDocked
from inventorycommon.util import IsModularShip
from localization import GetByLabel
import log
from utillib import KeyVal

class FittingBrowserListProvider(object):

    def __init__(self, onDropDataFunc):
        self.onDropDataFunc = onDropDataFunc
        self.fittingSvc = sm.GetService('fittingSvc')
        if session.role & ROLEMASK_ELEVATEDPLAYER:
            try:
                self.fittingSpawner = sm.GetService('fittingspawner')
            except:
                self.fittingSpawner = None

    def GetFittingScrolllist(self, *args):
        showPersonalFittings = settings.user.ui.Get('fitting_filter_ship_personalFittings', False)
        showCorpFittings = settings.user.ui.Get('fitting_filter_ship_corpFittings', False)
        filterOnFittings = showPersonalFittings or showCorpFittings
        personalFittings = self.fittingSvc.GetFittings(session.charid)
        corpFittings = self.fittingSvc.GetFittings(session.corpid)
        fittingNumByTypeID = self.GetNumShipsByTypeID(personalFittings, corpFittings)
        filterText = settings.user.ui.Get('fitting_fittingSearchField', '')
        filterTextLower = filterText.lower()
        fittings = self.FilterOutFittings(filterTextLower, personalFittings, corpFittings, showPersonalFittings, showCorpFittings)
        fittingsByGroupID, shipsByGroupID, shipGroups, shipsByGroupAndRaceIDs, fittingsByGroupAndRaceIDs = self.GetShipsAndGroups(filterTextLower, fittings)
        scrolllist = []
        noFittingsFound = len(fittings) == 0 and filterOnFittings
        if noFittingsFound:
            scrolllist.append(listentry.Get('Generic', data={'label': GetByLabel('UI/Common/NothingFound')}))
        else:
            shipScrollist = []
            for groupName, groupID in shipGroups:
                shipsForGroup = shipsByGroupAndRaceIDs[groupID]
                fittingsByRaceID = fittingsByGroupAndRaceIDs[groupID]
                data = {'GetSubContent': self.GetRacesForGroup,
                 'label': groupName,
                 'groupItems': shipsForGroup,
                 'fittingsByRaceID': fittingsByRaceID,
                 'shipsByRaceID': shipsForGroup,
                 'id': ('fittingMgmtScrollWndGroup', groupName),
                 'showicon': 'hide',
                 'showlen': 0,
                 'state': 'locked',
                 'BlockOpenWindow': 1,
                 'DropData': self.onDropDataFunc,
                 'fittingNumByTypeID': fittingNumByTypeID}
                groupEntry = (groupName, listentry.Get(entryType='Group', data=data))
                shipScrollist.append(groupEntry)

            shipScrollist = SortListOfTuples(shipScrollist)
            if shipScrollist:
                scrolllist.extend(shipScrollist)
            else:
                scrolllist.append(listentry.Get('Generic', data={'label': GetByLabel('UI/Common/NothingFound')}))
        return scrolllist

    def GetNumShipsByTypeID(self, personalFittings, corpFittings):
        fittingNumByTypeID = defaultdict(lambda : defaultdict(int))
        for isCorp, fittingDict in [(False, personalFittings), (True, corpFittings)]:
            for fitting in fittingDict.itervalues():
                fittingNumByTypeID[fitting.shipTypeID][isCorp] += 1

        return fittingNumByTypeID

    def GetRacesForGroup(self, nodedata):
        shipScrollist = []
        fittingsByRaceID = nodedata.fittingsByRaceID
        shipsByRaceID = nodedata.shipsByRaceID
        for raceID, fittingsForRace in nodedata.groupItems.iteritems():
            raceName = cfg.races.Get(raceID).raceName
            data = {'GetSubContent': self.GetShipGroupSubContent,
             'label': raceName,
             'fittings': fittingsByRaceID[raceID],
             'groupItems': fittingsForRace,
             'allShips': shipsByRaceID[raceID],
             'id': ('fittingMgmtScrollWndGroup', raceID),
             'iconID': cfg.races.Get(raceID).iconID,
             'state': 'locked',
             'BlockOpenWindow': 1,
             'DropData': self.onDropDataFunc,
             'sublevel': 1,
             'fittingNumByTypeID': nodedata.fittingNumByTypeID}
            groupEntry = (raceName, listentry.Get(entryType='Group', data=data))
            shipScrollist.append(groupEntry)

        shipScrollist = SortListOfTuples(shipScrollist)
        return shipScrollist

    def GetMaxFittingNumber(self, ownerID):
        maxFittings = None
        if ownerID == session.charid:
            maxFittings = const.maxCharFittings
        elif ownerID == session.corpid:
            maxFittings = const.maxCorpFittings
        return maxFittings

    def FilterOutFittings(self, filterTextLower, personalFittings, corpFittings, showPersonalFittings, showCorpFittings):
        fittings = {}
        if showPersonalFittings:
            fittings.update(personalFittings)
        if showCorpFittings:
            fittings.update(corpFittings)
        if not filterTextLower:
            return fittings
        validFittings = {}
        for fittingID, fitting in fittings.iteritems():
            if self.TextMatched(filterTextLower, fitting):
                validFittings[fittingID] = fitting

        return validFittings

    def TextMatched(self, filterTextLower, fitting):
        if self.MatchedWithFittingName(filterTextLower, fitting):
            return True
        if self.MatchedWithShipName(filterTextLower, fitting):
            return True
        return False

    def MatchedWithShipName(self, filterTextLower, fitting):
        shipTypeName = evetypes.GetName(fitting.shipTypeID)
        matchedWithShipName = shipTypeName.lower().find(filterTextLower) >= 0
        return matchedWithShipName

    def MatchedWithFittingName(self, filterTextLower, fitting):
        foundTextInFittingName = fitting.name.lower().find(filterTextLower) >= 0
        return foundTextInFittingName

    def GetShipsAndGroups(self, filterTextLower, fittings):
        fittingsByGroupID = defaultdict(list)
        fittingsByGroupAndRaceIDs = defaultdict(lambda : defaultdict(set))
        if not fittings:
            shipGroups, shipsByGroupID, shipsByGroupAndRaceIDs = self.GetAllShipGroupsAndShipsByGroupID(filterTextLower)
        else:
            shipGroups = set()
            shipsByGroupID = defaultdict(set)
            shipsByGroupAndRaceIDs = defaultdict(lambda : defaultdict(set))
        for fittingID, fitting in fittings.iteritems():
            shipTypeID = fitting.shipTypeID
            if not evetypes.Exists(shipTypeID):
                log.LogError('Ship in stored fittings does not exist, shipID=%s, fittingID=%s' % (shipTypeID, fittingID))
                continue
            groupID = evetypes.GetGroupID(shipTypeID)
            fittingsByGroupID[groupID].append(fitting)
            groupName = evetypes.GetGroupName(shipTypeID)
            shipGroups.add((groupName, groupID))
            raceID = evetypes.GetRaceID(shipTypeID)
            shipsByGroupAndRaceIDs[groupID][raceID].add(shipTypeID)
            fittingsByGroupAndRaceIDs[groupID][raceID].add(fitting)

        return (fittingsByGroupID,
         shipsByGroupID,
         shipGroups,
         shipsByGroupAndRaceIDs,
         fittingsByGroupAndRaceIDs)

    def GetAllShipGroupsAndShipsByGroupID(self, filterTextLower):
        shipGroups = set()
        shipsByGroupID = defaultdict(set)
        shipsByGroupAndRaceIDs = defaultdict(lambda : defaultdict(set))
        grouplist = sm.GetService('marketutils').GetMarketGroups()[const.marketCategoryShips]
        shipTypesIDsFromMarket = {i for i in itertools.chain.from_iterable([ x.types for x in grouplist ])}
        for shipTypeID in shipTypesIDsFromMarket:
            shipName = evetypes.GetName(shipTypeID)
            if filterTextLower and shipName.lower().find(filterTextLower) < 0:
                continue
            groupID = evetypes.GetGroupID(shipTypeID)
            groupName = evetypes.GetGroupName(shipTypeID)
            shipGroups.add((groupName, groupID))
            shipsByGroupID[groupID].add(shipTypeID)
            raceID = evetypes.GetRaceID(shipTypeID)
            shipsByGroupAndRaceIDs[groupID][raceID].add(shipTypeID)

        return (shipGroups, shipsByGroupID, shipsByGroupAndRaceIDs)

    def GetShipGroupSubContent(self, nodedata, *args):
        scrolllist = []
        fittingsByType = defaultdict(list)
        fittingNumByTypeID = nodedata.fittingNumByTypeID
        for fitting in nodedata.fittings:
            shipTypeID = fitting.shipTypeID
            if not evetypes.Exists(shipTypeID):
                log.LogError('Ship in stored fittings does not exist, shipID=%s, fittingID=%s' % (shipTypeID, fitting.fittingID))
                continue
            fittingsByType[shipTypeID].append(fitting)

        allShips = nodedata.allShips
        for typeID in allShips:
            typeName = evetypes.GetName(typeID)
            numPersonal = fittingNumByTypeID[typeID][False]
            numCorp = fittingNumByTypeID[typeID][True]
            fittingsForType = fittingsByType.get(typeID, [])
            entry = self.GetShipTypeGroup(typeID, typeName, fittingsForType, numPersonal, numCorp)
            scrolllist.append((typeName, entry))

        scrolllist = SortListOfTuples(scrolllist)
        return scrolllist

    def GetShipTypeGroup(self, typeID, typeName, fittingsForType, numPersonal, numCorp):
        label = '<b>%s</b>' % typeName
        label += '<br>Saved Fittings: %s / %s' % (numPersonal, numCorp)
        data = {'label': label,
         'typeID': typeID,
         'getIcon': True,
         'sublevel': 2,
         'maxLines': 2,
         'GetSubContent': self.GetFittingSubContent,
         'id': ('FittingShipTypeListGroup', typeID),
         'showlen': 0,
         'state': 'locked',
         'BlockOpenWindow': 1,
         'typeName': typeName,
         'fittings': fittingsForType,
         'numPersonal': numPersonal,
         'numCorp': numCorp}
        entry = listentry.Get(entryType=None, data=data, decoClass=FittingShipTypeListGroup)
        return entry

    def GetFittingSubContent(self, nodedata, *args):
        return self.GetFittingEntriesForType(nodedata.typeName, nodedata.fittings)

    def GetFittingEntriesForType(self, typeName, fittings, *args):
        scrolllist = []
        for eachFitting in fittings:
            fittingName = eachFitting.name
            if eachFitting.ownerID == session.corpid:
                fakeOwnerType = 1
            else:
                fakeOwnerType = 0
            data = {'label': fittingName,
             'fittingID': eachFitting.fittingID,
             'fitting': eachFitting,
             'ownerID': session.charid,
             'showinfo': 1,
             'showicon': 'hide',
             'sublevel': 3,
             'ignoreRightClick': 1,
             'OnClick': self.OnFittingClicked,
             'OnDropData': self.onDropDataFunc,
             'GetMenu': self.GetFittingMenu,
             'ownerType': fakeOwnerType}
            sortBy = (fakeOwnerType, fittingName.lower())
            entry = listentry.Get('FittingEntry', data=data)
            scrolllist.append((sortBy, entry))

        scrolllist = SortListOfTuples(scrolllist)
        return scrolllist

    def OnFittingClicked(self, entry, *args):
        fitting = entry.sr.node.fitting
        sm.GetService('ghostFittingSvc').SimulateFitting(fitting)

    def GetFittingMenu(self, entry):
        node = entry.sr.node
        node.scroll.SelectNode(node)
        selectedNodes = node.scroll.GetSelectedNodes(node)
        multiSelected = len(selectedNodes) > 1
        fittingID = entry.sr.node.fittingID
        ownerID = entry.sr.node.ownerID
        maxShipsAllowed = int(sm.GetService('machoNet').GetGlobalConfig().get('bulkFit_maxShips', 30))
        m = []
        if not multiSelected:
            m += [('Simulate Fitting', self.OnFittingClicked, [entry])]
            m += [(MenuLabel('UI/Fitting/FittingWindow/FittingManagement/LoadFitting'), self.fittingSvc.LoadFittingFromFittingID, [ownerID, fittingID])]
            if maxShipsAllowed and IsDocked() and not IsModularShip(entry.sr.node.fitting.shipTypeID):
                m += [(MenuLabel('UI/Fitting/FittingWindow/FittingManagement/OpenMultifit'), self.DoBulkFit, [entry])]
        m += [None]
        m += [(GetByLabel('UI/Fitting/FittingWindow/FittingManagement/DeleteFitting'), self.DeleteFitting, [entry, selectedNodes])]
        return m

    def DeleteFitting(self, entry, selectedNodes):
        if eve.Message('DeleteFitting', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
        fittingID = entry.sr.node.fittingID
        ownerID = entry.sr.node.ownerID
        sm.GetService('fittingSvc').DeleteFitting(ownerID, fittingID)

    def DoBulkFit(self, entry):
        fitting = entry.sr.node.fitting
        OpenOrLoadMultiFitWnd(fitting)


class FittingShipTypeListGroup(Group):
    iconSize = 32
    default_iconSize = iconSize
    isDragObject = True

    def Startup(self, *etc):
        Group.Startup(self, etc)
        self.sr.label.maxLines = 2
        self.techIcon = Sprite(name='techIcon', parent=self, left=1, width=16, height=16, idx=0)
        texturePath = 'res:/UI/Texture/classes/Fitting/iconSimulatorToggle.png'
        iconSize = 24
        switchCont = Container(name='switchCont', parent=self, align=uiconst.TORIGHT, width=iconSize, padRight=4)
        simulateBtn = ButtonIcon(texturePath=texturePath, parent=switchCont, align=uiconst.CENTERLEFT, pos=(0,
         0,
         iconSize,
         iconSize), func=self.SimulateShip, iconSize=iconSize)

    def Load(self, node):
        Group.Load(self, node)
        typeID = node.typeID
        self.sr.icon.LoadIconByTypeID(typeID=typeID, size=self.iconSize, ignoreSize=True, isCopy=False)
        self.sr.icon.SetSize(self.iconSize, self.iconSize)
        techSprite = uix.GetTechLevelIcon(self.techIcon, 1, typeID)
        self.techIcon.left = self.sr.icon.left
        self.sr.label.left = self.sr.icon.left + self.sr.icon.width + 4

    def SimulateShip(self):
        ghostFittingSvc = sm.GetService('ghostFittingSvc')
        shipTypeID = self.sr.node.typeID
        ghostFittingSvc.LoadSimulatedFitting(shipTypeID, [])

    def GetHeight(self, *args):
        node, _ = args
        textwidth, textheight = EveLabelMedium.MeasureTextSize(node.label, maxLines=2)
        node.height = textheight + 6
        return node.height

    def GetMenu(self):
        typeID = self.sr.node.typeID
        return sm.GetService('menu').GetMenuFormItemIDTypeID(None, typeID, ignoreMarketDetails=False)

    def GetDragData(self):
        typeID = self.sr.node.typeID
        keyVal = KeyVal(__guid__='listentry.GenericMarketItem', typeID=typeID, label=evetypes.GetName(typeID))
        return [keyVal]

    def LoadTooltipPanel(self, tooltipPanel, *args):
        node = self.sr.node
        typeID = node.typeID
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.AddLabelLarge(text='<b>%s</b>' % evetypes.GetName(typeID))
        numPersonalText = '  .Personal fittings : %s' % node.numPersonal
        numCorpText = '  .Corp fittings : %s' % node.numCorp
        tooltipPanel.AddLabelMedium(text=numPersonalText)
        tooltipPanel.AddLabelMedium(text=numCorpText)
        if HasTraits(typeID):
            tooltipPanel.AddSpacer(width=300, height=1)
            TraitsContainer(parent=tooltipPanel, typeID=typeID, padding=7)
