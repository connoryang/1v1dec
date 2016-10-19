#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\infoPanels\infoPanelLocationInfo.py
from collections import defaultdict
import evetypes
from carbonui.primitives.container import Container
from entosis.occupancyCalculator import GetOccupancyMultiplier
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from sovDashboard import ShouldUpdateStructureInfo, GetSovStructureInfoByTypeID
from sovDashboard.dashboardConst import UNCLAIMABLE
from sovDashboard.dashboardSovHolderIcon import SovHolderIcon
from sovDashboard.defenseMultiplierIcon import DefenseMultiplierIcon
import uicontrols
from eve.client.script.ui.shared.infoPanels.InfoPanelBase import InfoPanelBase
import uicls
import carbonui.const as uiconst
from uthread2 import call_after_simtime_delay
import util
import localization
import infoPanelConst
import uiutil
import telemetry
import base
import bookmarkUtil
import uix
import const
from utillib import KeyVal
import log

class InfoPanelLocationInfo(InfoPanelBase):
    __guid__ = 'uicls.InfoPanelLocationInfo'
    default_name = 'InfoPanelLocationInfo'
    panelTypeID = infoPanelConst.PANEL_LOCATION_INFO
    label = 'UI/Neocom/SystemInfo'
    default_iconTexturePath = 'res:/UI/Texture/Classes/InfoPanels/LocationInfo.png'
    __notifyevents__ = InfoPanelBase.__notifyevents__[:]
    __notifyevents__.extend(['OnSolarsystemSovStructureChanged', 'OnCapitalSystemChanged'])

    def ApplyAttributes(self, attributes):
        uicls.InfoPanelBase.ApplyAttributes(self, attributes)
        self.facwarSvc = sm.GetService('facwar')
        self.sovSvc = sm.GetService('sov')
        self.validNearBy = [const.groupAsteroidBelt,
         const.groupMoon,
         const.groupPlanet,
         const.groupWarpGate,
         const.groupStargate]
        self.nearby = None
        self.locationTimer = None
        self.lastLocationID = None
        self.sovHolderIcons = []
        self.bonusIcon = None
        self.headerLabel = self.headerCls(name='header', parent=self.headerCont, align=uiconst.CENTERLEFT)
        self.headerLabel.SetRightAlphaFade(infoPanelConst.PANELWIDTH - infoPanelConst.LEFTPAD, self.HEADER_FADE_WIDTH)
        self.tidiIndicator = uicls.tidiIndicator(parent=self.headerCont, name='tidiIndicator', align=uiconst.CENTERLEFT, pos=(0, 0, 24, 24))
        self.nearestLocationInfo = uicontrols.EveLabelMedium(name='nearestLocationInfo', parent=self.mainCont, align=uiconst.TOTOP)
        self.sovInfoContainer = Container(parent=self.mainCont, align=uiconst.TOTOP, height=42, padTop=2)

    @staticmethod
    def IsAvailable():
        return True

    def ConstructHeaderButton(self):
        btn = ListSurroundingsBtn(parent=self.headerBtnCont, align=uiconst.TOPRIGHT, pos=(0,
         0,
         self.topCont.height,
         self.topCont.height), texturePath=self.default_iconTexturePath, iconSize=16, showIcon=True)
        btn.hint = localization.GetByLabel('UI/Neocom/ListItemsInSystem')
        btn.sr.owner = self
        btn.sr.groupByType = 1
        btn.filterCurrent = 1
        btn.sr.itemID = session.solarsystemid2
        btn.sr.typeID = const.typeSolarSystem
        return btn

    def ConstructNormal(self):
        self.UpdateLocationInfo()

    def ConstructCompact(self):
        self.UpdateMainLocationInfo()

    @telemetry.ZONE_METHOD
    def UpdateLocationInfo(self):
        if eve.session.solarsystemid2 and session.charid:
            self.UpdateMainLocationInfo()
            self.UpdateNearestOrStationLocationInfo()
            self.UpdateSOVLocationInfo()

    @telemetry.ZONE_METHOD
    def UpdateMainLocationInfo(self):
        if session.solarsystemid2:
            self.headerLabel.text = sm.GetService('infoPanel').GetSolarSystemTrace(session.solarsystemid2, localization.GetByLabel('UI/Neocom/Autopilot/CurrentLocationType', itemType=const.typeSolarSystem))
            self.headerLabel.state = uiconst.UI_NORMAL
            self.tidiIndicator.left = self.headerLabel.left + self.headerLabel.textwidth + 4
            solarsystemitems = sm.GetService('map').GetSolarsystemItems(session.solarsystemid2, True, False)
            self.headerButton.sr.mapitems = solarsystemitems
            self.headerButton.solarsystemid = session.solarsystemid2
            self.headerButton.sr.itemID = session.solarsystemid2
            self.headerButton.sr.typeID = const.typeSolarSystem

    @telemetry.ZONE_METHOD
    def UpdateNearestOrStationLocationInfo(self, nearestBall = None):
        infoSettings = sm.GetService('infoPanel').GetLocationInfoSettings()
        nearestOrStationLabel = ''
        if 'nearest' in infoSettings and session.solarsystemid2:
            if session.stationid2 or session.structureid:
                try:
                    if session.stationid2:
                        itemID = session.stationid2
                        typeID = eve.stationItem.stationTypeID
                    else:
                        itemID = session.structureid
                        typeID = sm.GetService('invCache').GetInventory(const.containerStructure).GetTypeID()
                    stationName = cfg.evelocations.Get(itemID).name
                    nearestOrStationLabel = "<url=showinfo:%d//%d alt='%s'>%s</url>" % (typeID,
                     itemID,
                     localization.GetByLabel('UI/Generic/CurrentStation'),
                     stationName)
                except AttributeError as e:
                    log.LogException('Failed when getting station/structure name')

            else:
                nearestBall = nearestBall or self.GetNearestBall()
                if nearestBall:
                    self.nearby = nearestBall.id
                    slimItem = sm.StartService('michelle').GetItem(nearestBall.id)
                    if slimItem:
                        nearestOrStationLabel = "<url=showinfo:%d//%d alt='%s'>%s</url>" % (slimItem.typeID,
                         slimItem.itemID,
                         localization.GetByLabel('UI/Neocom/Nearest'),
                         cfg.evelocations.Get(nearestBall.id).locationName)
                if self.locationTimer is None:
                    self.locationTimer = base.AutoTimer(1313, self.CheckNearest)
        if nearestOrStationLabel:
            self.nearestLocationInfo.text = nearestOrStationLabel
            self.nearestLocationInfo.state = uiconst.UI_NORMAL
        else:
            self.nearestLocationInfo.state = uiconst.UI_HIDDEN

    def FlushSovInfoContainer(self):
        self.sovInfoContainer.Flush()
        self.sovHolderIcons = []

    @telemetry.ZONE_METHOD
    def UpdateSOVLocationInfo(self):
        self.FlushSovInfoContainer()
        infoSettings = sm.GetService('infoPanel').GetLocationInfoSettings()
        if 'sovereignty' in infoSettings and session.solarsystemid2:
            self.sovInfoContainer.display = True
            if util.IsWormholeRegion(session.regionid):
                self.DrawWormholeInfo()
                return
            isFacWar = self.facwarSvc.IsFacWarSystem(session.solarsystemid2)
            factionID = self._GetSolarsystemFactionID(session.solarsystemid2, isFacWar)
            if factionID:
                self.DrawUnclaimableSystemInfo(factionID, isFacWar=isFacWar)
            else:
                solarsystemStructureInfo = self.sovSvc.GetSovStructuresInfoForSolarSystem(session.solarsystemid2)
                self.DrawClaimableSystemInfo(solarsystemStructureInfo)
        else:
            self.sovInfoContainer.display = False

    def _GetSolarsystemFactionID(self, solarsystemID, isFacWar = False):
        if isFacWar:
            factionID = self.facwarSvc.GetSystemOccupier(solarsystemID)
            return factionID
        solarSystem = cfg.mapSystemCache.get(solarsystemID, None)
        if solarSystem:
            return getattr(solarSystem, 'factionID', None)

    def GetAllianceIDFromCorpID(self, corpID):
        if corpID:
            return sm.GetService('corp').GetCorporation(corpID).allianceID

    def ShowMultiplyBonusesIcon(self, parent, isCapital, left, capitalOwnerID):
        devIndexInfo = self.sovSvc.GetIndexInfoForSolarsystem(session.solarsystemid2)
        multiplier = 1 / GetOccupancyMultiplier(devIndexInfo.industrialIndexLevel, devIndexInfo.militaryIndexLevel, devIndexInfo.strategicIndexLevel, isCapital)
        devIndexLevelInfo = (devIndexInfo.militaryIndexLevel, devIndexInfo.industrialIndexLevel, devIndexInfo.strategicIndexLevel)
        if self.bonusIcon and not self.bonusIcon.destroyed:
            self.bonusIcon.SetStatusFromMultiplier(multiplier, devIndexLevelInfo)
            self.bonusIcon.ChangeCapitalState(isCapital=isCapital)
        else:
            self.bonusIcon = DefenseMultiplierIcon(parent=parent, iconSize=32, align=uiconst.CENTERLEFT, pos=(left,
             0,
             60,
             60), currentMultiplier=multiplier, devIndexes=devIndexLevelInfo, isCapital=isCapital, capitalOwnerID=capitalOwnerID)

    def DrawWormholeInfo(self):
        self.sovInfoContainer.height = 10
        EveLabelMedium(parent=self.sovInfoContainer, text=localization.GetByLabel('UI/Neocom/Unclaimable'), align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)

    def DrawUnclaimableSystemInfo(self, factionID, isFacWar = None):
        tcuIcon = SovHolderIcon(parent=self.sovInfoContainer, align=uiconst.CENTERLEFT, structureInfo=KeyVal(typeID=const.typeTerritorialClaimUnit, solarSystemID=session.solarsystemid2, ownerID=factionID))
        factionText = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=cfg.eveowners.Get(factionID).name, info=('showinfo', const.typeFaction, factionID))
        if isFacWar:
            facState = sm.GetService('infoPanel').GetSolarSystemStatusText()
            factionText = '%s %s' % (factionText, facState)
        EveLabelMedium(parent=self.sovInfoContainer, text=factionText, left=tcuIcon.width + 4, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)

    def DrawClaimableSystemInfo(self, solarsystemStructureInfo):
        structureInfosByTypeID = GetSovStructureInfoByTypeID(solarsystemStructureInfo)

        def GetMouseDownFunction(sovHolderIcon):

            def OnMouseDownFunction(button):
                SovHolderIcon.OnMouseDown(sovHolderIcon, button)
                itemID = sovHolderIcon.structureInfo.get('itemID', None)
                if itemID:
                    sm.GetService('menu').TryExpandActionMenu(itemID, sovHolderIcon)

            return OnMouseDownFunction

        xPos = -4
        for structureTypeID, structureInfo in structureInfosByTypeID.iteritems():
            sovHolderIcon = SovHolderIcon(parent=self.sovInfoContainer, left=xPos, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, structureInfo=structureInfo, showStructureStatusBar=True)
            sovHolderIcon.OnMouseDown = GetMouseDownFunction(sovHolderIcon)
            self.sovHolderIcons.append(sovHolderIcon)
            xPos += sovHolderIcon.width + 6

        tcuInfo = structureInfosByTypeID[const.typeTerritorialClaimUnit]
        isCapital = tcuInfo.get('isCapital', False)
        capitalOwnerID = tcuInfo.get('allianceID', None)
        self.ShowMultiplyBonusesIcon(self.sovInfoContainer, isCapital, xPos, capitalOwnerID)

    def CheckNearest(self):
        if not session.solarsystemid or not self.headerLabel:
            self.locationTimer = None
            return
        nearestBall = self.GetNearestBall()
        if nearestBall and self.nearby != nearestBall.id:
            self.UpdateNearestOrStationLocationInfo(nearestBall)

    def GetNearestBall(self, fromBall = None, getDist = 0):
        ballPark = sm.GetService('michelle').GetBallpark()
        if not ballPark:
            return
        lst = []
        for ballID, ball in ballPark.balls.iteritems():
            slimItem = ballPark.GetInvItem(ballID)
            if slimItem and slimItem.groupID in self.validNearBy:
                if fromBall:
                    dist = trinity.TriVector(ball.x - fromBall.x, ball.y - fromBall.y, ball.z - fromBall.z).Length()
                    lst.append((dist, ball))
                else:
                    lst.append((ball.surfaceDist, ball))

        lst.sort()
        if getDist:
            return lst[0]
        if lst:
            return lst[0][1]

    def OnSolarsystemSovStructureChanged(self, solarsystemID, whatChanged, sourceItemID = None):
        if sourceItemID is None:
            if session.solarsystemid2 == solarsystemID and session.charid:
                self.UpdateSOVLocationInfo()
            return
        for buttonIcon in self.sovHolderIcons:
            if ShouldUpdateStructureInfo(buttonIcon.structureInfo, sourceItemID):
                newStructureInfo = self.sovSvc.GetSpecificSovStructuresInfoInSolarSystem(solarsystemID, sourceItemID)
                buttonIcon.SolarsystemSovStructureChanged(sourceItemID, newStructureInfo, whatChanged)
                return

    def OnCapitalSystemChanged(self, change):
        allianceID, oldSolarSystemID, newSolarSystemID = change
        if oldSolarSystemID is None:
            call_after_simtime_delay(self.UpdateSOVLocationInfo, 30)
        else:
            self.UpdateSOVLocationInfo()

    def OnPostCfgDataChanged(self, what, data):
        if what == 'evelocations':
            self.UpdateLocationInfo()


class ListSurroundingsBtn(uicontrols.ButtonIcon):
    __guid__ = 'xtriui.ListSurroundingsBtn'
    __update_on_reload__ = 1
    isDragObject = True
    default_iconSize = 24
    default_name = 'ListSurroundingsBtn'
    default_texturePath = 'res:/ui/texture/icons/77_32_49.png'

    def ApplyAttributes(self, attributes):
        uicontrols.ButtonIcon.ApplyAttributes(self, attributes)
        self.expandOnLeft = 1
        self.itemssorted = 0
        self.filterCurrent = 1
        if not attributes.showIcon:
            self.icon.Hide()

    def ShowMenu(self, *args):
        print 'SHOW'

    def GetInt(self, string):
        value = filter(lambda x: x in '0123456789', string)
        try:
            value = int(value)
        except:
            sys.exc_clear()

        return value

    def CelestialMenu(self, *args):
        return sm.GetService('menu').CelestialMenu(*args)

    def ExpandCelestial(self, mapItem):
        return sm.GetService('menu').CelestialMenu(mapItem.itemID, mapItem=mapItem)

    def ExpandTypeMenu(self, items):
        typemenu = []
        for item in items:
            if item.groupID == const.groupStation:
                name = cfg.evelocations.Get(item.itemID).name
                entryName = uix.EditStationName(name, 1)
            else:
                entryName = cfg.evelocations.Get(item.itemID).name or item.itemName or 'no name!'
            escapeSorter = roman = typeName = None
            sequence = ''
            typemenu.append(((item.celestialIndex, item.orbitIndex, entryName), (entryName, ('isDynamic', self.ExpandCelestial, (item,)))))

        typemenu = uiutil.SortListOfTuples(typemenu)
        return typemenu

    def GetMenu(self, *args):
        if eve.rookieState and eve.rookieState < 32:
            return []
        m = []
        if self.sr.Get('groupByType', 0):
            if self.sr.typeID and self.sr.itemID:
                m += [(uiutil.MenuLabel('UI/Commands/ShowInfo'), sm.GetService('menu').ShowInfo, (self.sr.typeID, self.sr.itemID))]

            def GetGroupingKeyVal(labelPath):
                return util.KeyVal(labelPath=labelPath, typeIDs=[])

            groupDict = {const.groupAsteroidBelt: GetGroupingKeyVal('UI/Common/LocationTypes/AsteroidBelts'),
             const.groupPlanet: GetGroupingKeyVal('UI/Common/LocationTypes/Planets'),
             const.groupStargate: GetGroupingKeyVal('UI/Common/LocationTypes/Stargates'),
             const.groupStation: GetGroupingKeyVal('UI/Common/LocationTypes/Stations')}
            categoryDict = {const.categoryStructure: GetGroupingKeyVal('UI/Common/LocationTypes/Structures')}
            for item in self.sr.mapitems:
                if item.groupID in groupDict:
                    groupDict[item.groupID].typeIDs.append(item)
                categoryID = evetypes.GetCategoryID(item.typeID)
                if categoryID in categoryDict:
                    categoryDict[categoryID].typeIDs.append(item)

            menuItemDict = {}
            menuItemDict.update(groupDict)
            menuItemDict.update(categoryDict)
            listToSort = []
            for groupingID, groupingInfo in menuItemDict.iteritems():
                itemList = groupingInfo.typeIDs
                if not itemList:
                    continue
                labelPath = groupingInfo.labelPath
                menuLabel = uiutil.MenuLabel(labelPath)
                listToSort.append((localization.GetByLabel(labelPath), (menuLabel, itemList)))

            sortedList = uiutil.SortListOfTuples(listToSort)
            for entry in sortedList:
                menuLabel, itemList = entry
                m.append((menuLabel, ('isDynamic', self.ExpandTypeMenu, (itemList,))))

            bookmarks = {}
            folders = {}
            b, f = sm.GetService('bookmarkSvc').GetBookmarksAndFolders()
            bookmarks.update(b)
            folders.update(f)
            bookmarkMenu = bookmarkUtil.GetBookmarkMenuForSystem(bookmarks, folders)
            if bookmarkMenu:
                m += bookmarkMenu
            agentMenu = sm.GetService('journal').GetMyAgentJournalBookmarks()
            if agentMenu:
                agentMenu2 = []
                for missionNameID, bms, agentID in agentMenu:
                    if isinstance(missionNameID, (int, long)):
                        missionName = localization.GetByMessageID(missionNameID)
                    else:
                        missionName = missionNameID
                    agentMenuText = uiutil.MenuLabel('UI/Neocom/MissionNameSubmenu', {'missionName': missionName,
                     'agent': agentID})
                    tmp = [agentMenuText, []]
                    for bm in bms:
                        if bm.solarsystemID == session.solarsystemid2:
                            txt = bm.hint
                            systemName = cfg.evelocations.Get(bm.solarsystemID).name
                            if bm.locationType == 'dungeon':
                                txt = txt.replace(' - %s' % systemName, '')
                            if '- Moon ' in txt:
                                txt = txt.replace(' - Moon ', ' - M')
                            if txt.endswith('- '):
                                txt = txt[:-2]
                            tmp[1].append((txt, ('isDynamic', self.CelestialMenu, (bm.itemID,
                               None,
                               None,
                               0,
                               None,
                               None,
                               bm))))

                    if tmp[1]:
                        agentMenu2.append(tmp)

                if agentMenu2:
                    agentMenuText = uiutil.MenuLabel('UI/Neocom/AgentMissionsSubmenu')
                    m += [None, (agentMenuText, lambda : None)] + agentMenu2
            contractsMenu = sm.GetService('contracts').GetContractsBookmarkMenu()
            if contractsMenu:
                m += contractsMenu
        else:
            if not self.itemssorted:
                self.sr.mapitems = uiutil.SortListOfTuples([ (item.itemName.lower(), item) for item in self.sr.mapitems ])
                self.itemssorted = 1
            maxmenu = 25
            if len(self.sr.mapitems) > maxmenu:
                groups = []
                approxgroupcount = len(self.sr.mapitems) / float(maxmenu)
                counter = 0
                while counter < len(self.sr.mapitems):
                    groups.append(self.sr.mapitems[counter:counter + maxmenu])
                    counter = counter + maxmenu

                for group in groups:
                    groupmenu = []
                    for item in group:
                        groupmenu.append((item.itemName or 'no name!', self.CelestialMenu(item.itemID, item)))

                    if len(groupmenu):
                        fromLetter = '???'
                        if group[0].itemName:
                            fromLetter = uiutil.StripTags(group[0].itemName)[0]
                        toLetter = '???'
                        if group[-1].itemName:
                            toLetter = uiutil.StripTags(group[-1].itemName)[0]
                        m.append((fromLetter + '...' + toLetter, groupmenu))

                return m
            for item in self.sr.mapitems[:30]:
                m.append((item.itemName or 'no name!', self.CelestialMenu(item.itemID, item)))

        m.append(None)
        starmapSvc = sm.GetService('starmap')
        showRoute = settings.user.ui.Get('neocomRouteVisible', 1)
        infoSettings = sm.GetService('infoPanel').GetLocationInfoSettings()
        if len(starmapSvc.GetWaypoints()) > 0:
            m.append((uiutil.MenuLabel('UI/Neocom/ClearAllAutopilotWaypoints'), starmapSvc.ClearWaypoints, (None,)))
        m.append(None)
        m.append((uiutil.MenuLabel('UI/Neocom/ConfigureSubmenu'), self.ConfigureLocationInfo))
        return m

    def DoWarpToHidden(self, instanceID):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None:
            bp.CmdWarpToStuff('epinstance', instanceID)

    def DoTutorial(self):
        bp = sm.GetService('michelle').GetRemotePark()
        if bp is not None and sm.GetService('space').CanWarp(forTut=True):
            eve.Message('Command', {'command': localization.GetByLabel('UI/Neocom/WarpingToTutorialSide')})
            bp.WarpToTutorial()

    def GetDragData(self, *args):
        itemID = self.sr.Get('itemID', None)
        typeID = self.sr.Get('typeID', None)
        if not itemID or not typeID:
            return []
        label = ''
        if typeID in (const.typeRegion, const.typeConstellation, const.typeSolarSystem):
            label += cfg.evelocations.Get(itemID).name
            elabel = {const.typeRegion: localization.GetByLabel('UI/Neocom/Region'),
             const.typeConstellation: localization.GetByLabel('UI/Neocom/Constellation'),
             const.typeSolarSystem: localization.GetByLabel('UI/Neocom/SolarSystem')}
            label += ' %s' % elabel.get(typeID)
        entry = util.KeyVal()
        entry.itemID = itemID
        entry.typeID = typeID
        entry.__guid__ = 'xtriui.ListSurroundingsBtn'
        entry.label = label
        return [entry]

    @telemetry.ZONE_METHOD
    def ConfigureLocationInfo(self):
        label = localization.GetByLabel('UI/Neocom/ConfigureWoldInfoText')
        setting = 'neocomLocationInfo_3'
        valid = ['nearest', 'sovereignty']
        current = sm.GetService('infoPanel').GetLocationInfoSettings()
        itemMapping = [util.KeyVal(name='nearest', label='%s / %s' % (localization.GetByLabel('UI/Neocom/Nearest'), localization.GetByLabel('UI/Neocom/DockedIn'))), util.KeyVal(name='sovereignty', label=localization.GetByLabel('UI/Neocom/Sovereignty'))]
        format = [{'type': 'text',
          'text': label}, {'type': 'push'}]
        for info in itemMapping:
            if info.name not in valid:
                continue
            format.append({'type': 'checkbox',
             'setvalue': bool(info.name in current),
             'key': info.name,
             'label': '_hide',
             'required': 1,
             'text': info.label,
             'onchange': self.ConfigCheckboxChange})

        format += [{'type': 'push'}]
        caption = localization.GetByLabel('UI/Neocom/UpdateLocationSettings')
        retval = uix.HybridWnd(format, caption, 1, buttons=uiconst.OK, minW=240, minH=100, icon='res:/ui/Texture/WindowIcons/charactersheet.png', unresizeAble=1)
        if retval:
            newsettings = []
            for k, v in retval.iteritems():
                if v == 1:
                    newsettings.append(k)

            settings.char.windows.Set(setting, newsettings)

    def ConfigCheckboxChange(self, checkbox, *args):
        if checkbox.data['key'] in ('nearest', 'sovereignty'):
            current = sm.GetService('infoPanel').GetLocationInfoSettings()
            if checkbox.GetValue():
                if checkbox.data['key'] not in current:
                    current.append(checkbox.data['key'])
            elif checkbox.data['key'] in current:
                current.remove(checkbox.data['key'])
            settings.char.windows.Set('neocomLocationInfo_3', current)
            sm.GetService('infoPanel').UpdatePanel(infoPanelConst.PANEL_LOCATION_INFO)
