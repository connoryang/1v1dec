#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\assets\assetSafetyDeliverWindow.py
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbonui import const as uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.line import Line
from carbonui.uicore import uicorebase as uicore
from carbonui.util.color import Color
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.control.eveLabel import EveLabelLargeBold, EveLabelMedium, EveLabelMediumBold
from eve.client.script.ui.control.eveWindow import Window
import evetypes
from localization import GetByLabel
from localization.formatters import FormatTimeIntervalShortWritten
import uthread
import blue
MAX_STATIONCONT_HEIGHT = 500

class AssetSafetyDeliverWindow(Window):
    __guid__ = 'form.AssetSafetyDeliverWindow'
    default_width = 600
    default_height = 100
    default_windowID = 'AssetSafetyDeliverWindow'
    default_topParentHeight = 0
    default_clipChildren = True
    default_isPinable = False
    LINE_COLOR = (1, 1, 1, 0.2)
    BLUE_COLOR = (0.0, 0.54, 0.8, 1.0)
    GREEN_COLOR = (0.0, 1.0, 0.0, 0.8)
    GRAY_COLOR = Color.GRAY5
    PADDING = 15

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.solarSystemID = attributes.solarSystemID
        self.assetWrapID = attributes.assetWrapID
        self.nearestNPCStationInfo = attributes.nearestNPCStationInfo
        self.autoDeliveryTimestamp = attributes.autoDeliveryTimestamp
        self.manualDeliveryTimestamp = attributes.manualDeliveryTimestamp
        self.Layout()
        uthread.new(self.ReloadContent)

    def Layout(self):
        self.MakeUnMinimizable()
        self.HideHeader()
        self.MakeUnResizeable()
        self.container = ContainerAutoSize(parent=self.GetMainArea(), align=uiconst.TOTOP, alignMode=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, padding=(self.PADDING,
         self.PADDING,
         self.PADDING,
         self.PADDING), callback=self.OnContainerResized)
        text = GetByLabel('UI/Inventory/AssetSafety/DeliverToStation')
        header = EveLabelLargeBold(parent=self.container, align=uiconst.TOTOP, text=text)
        self.explanationLabel = EveLabelMedium(parent=self.container, align=uiconst.TOTOP, text='', color=self.GRAY_COLOR, padding=(0, 0, 0, 15), state=uiconst.UI_NORMAL)
        Line(parent=self.container, align=uiconst.TOTOP, color=self.LINE_COLOR)
        self.sameSolarSystemParent = ScrollContainer(parent=self.container, align=uiconst.TOTOP)
        self.sameSolarSystem = ContainerAutoSize(parent=self.sameSolarSystemParent, align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
        self.nearestStationLabel = EveLabelMedium(parent=self.container, align=uiconst.TOTOP, text='', color=self.GRAY_COLOR, padding=(0, 0, 0, 0))
        self.closeButton = Button(parent=self.container, label=GetByLabel('UI/Generic/Cancel'), func=self.Close, align=uiconst.TOTOP, fontsize=13, padding=(220, 10, 220, 0))
        uicore.animations.FadeTo(self.container, startVal=0.0, endVal=1.0, duration=0.5)

    def SetText(self, systemStations):
        solarSystemName = GetShowInfoLink(const.typeSolarSystem, cfg.evelocations.Get(self.solarSystemID).name, self.solarSystemID)
        now = blue.os.GetWallclockTime()
        timeUntilAuto = FormatTimeIntervalShortWritten(long(max(0, self.autoDeliveryTimestamp - now)))
        nearestNPCStationText = GetShowInfoLink(self.nearestNPCStationInfo['typeID'], self.nearestNPCStationInfo['name'], self.nearestNPCStationInfo['itemID'])
        stationsInSystem = len(systemStations)
        if self.manualDeliveryTimestamp - now < 0:
            if stationsInSystem:
                path = 'UI/Inventory/AssetSafety/DeliveryExplanationText'
            else:
                path = 'UI/Inventory/AssetSafety/DeliveryExplanationTextNoStations'
            text = GetByLabel(path, solarSystemName=solarSystemName, npcStationName=nearestNPCStationText, timeUntil=timeUntilAuto)
        else:
            timeUntilManual = FormatTimeIntervalShortWritten(long(max(0, self.manualDeliveryTimestamp - now)))
            if stationsInSystem:
                path = 'UI/Inventory/AssetSafety/DeliveryNotAvailableNowExplanationText'
            else:
                path = 'UI/Inventory/AssetSafety/DeliveryNotAvailableTextNoStations'
            text = GetByLabel(path, solarSystemName=solarSystemName, timUntilManualDelivery=timeUntilManual, npcStationName=nearestNPCStationText, timeUntilAutoDelivery=timeUntilAuto)
        self.explanationLabel.text = text

    def OnContainerResized(self):
        self.width = self.default_width
        self.height = self.container.height + self.PADDING * 2

    def ReloadContent(self):
        if self.destroyed:
            return
        self.sameSolarSystem.DisableAutoSize()
        self.sameSolarSystem.Flush()
        systemStations, nearestNPCStation = sm.RemoteSvc('structureAssetSafety').GetStructuresICanDeliverTo(self.solarSystemID)
        self.SetText(systemStations)
        if systemStations:
            stationIDs = [ station['itemID'] for station in systemStations ]
            cfg.evelocations.Prime(stationIDs)
            stations = [ s for s in systemStations if evetypes.GetCategoryID(s['typeID'] == const.categoryStation) ]
            sortedStations = GetSortedStationList(self.solarSystemID, systemStations)
            otherStructures = GetSortedStructures(self.solarSystemID, systemStations)
            buttonIsDisabled = self.manualDeliveryTimestamp - blue.os.GetWallclockTime() > 0
            for each in otherStructures + sortedStations:
                self.AddStation(each, buttonIsDisabled)

        self.sameSolarSystem.EnableAutoSize()
        self.sameSolarSystemParent.height = min(MAX_STATIONCONT_HEIGHT, self.sameSolarSystem.height)

    def AddStation(self, station, buttonIsDisabled):
        parent = self.sameSolarSystem
        container = ContainerAutoSize(parent=parent, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, bgColor=(0.2, 0.2, 0.2, 0.3))
        container.DisableAutoSize()
        label = GetShowInfoLink(station['typeID'], station['name'], station['itemID'])
        EveLabelMediumBold(parent=container, height=30, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, text=label, padding=(7, 8, 140, 5))
        btn = Button(parent=container, label=GetByLabel('UI/Inventory/AssetSafety/DeliverBtn'), align=uiconst.CENTERRIGHT, fontsize=13, fixedwidth=140, fixedheight=25, pos=(5, 0, 0, 0), func=self.DoDeliver, args=station['itemID'])
        if buttonIsDisabled:
            btn.Disable()
        Line(parent=parent, align=uiconst.TOTOP, color=self.LINE_COLOR)
        container.EnableAutoSize()

    def DoDeliver(self, *args):
        if eve.Message('SureYouWantToMoveAssetSafetyItemsToLocation', {}, uiconst.YESNO) != uiconst.ID_YES:
            return
        try:
            sm.RemoteSvc('structureAssetSafety').MoveSafetyWrapToStructure(self.assetWrapID, self.solarSystemID, destinationID=args[0])
        finally:
            AssetSafetyDeliverWindow.CloseIfOpen()

        sm.GetService('objectCaching').InvalidateCachedMethodCall('structureAssetSafety', 'GetStructuresICanDeliverTo')
        sm.GetService('objectCaching').InvalidateCachedMethodCall('structureAssetSafety', 'GetItemsInSafety')


def GetSortedStationList(solarSystemID, systemStations):
    stations = [ s for s in systemStations if evetypes.GetCategoryID(s['typeID']) == const.categoryStation ]
    solarsystemItems = {s.itemID:s for s in sm.GetService('map').GetSolarsystemItems(solarSystemID)}
    sortedStations = []
    for eachStation in stations:
        stationInfo = solarsystemItems.get(eachStation['itemID'], None)
        if stationInfo is None:
            continue
        eachStation['name'] = stationInfo.itemName
        sortValue = (stationInfo.celestialIndex, stationInfo.orbitIndex, stationInfo.itemName.lower())
        sortedStations.append((sortValue, eachStation))

    sortedStations = SortListOfTuples(sortedStations)
    return sortedStations


def GetSortedStructures(solarSystemID, systemStations):
    strucutres = [ s for s in systemStations if evetypes.GetCategoryID(s['typeID']) != const.categoryStation ]
    sortedStructures = []
    for eachStructure in strucutres:
        try:
            name = cfg.evelocations.Get(eachStructure['itemID']).locationName
        except KeyError:
            name = None

        if not name:
            name = '%s - %s' % (cfg.evelocations.Get(solarSystemID).name, evetypes.GetName(eachStructure['typeID']))
        eachStructure['name'] = name
        sortedStructures.append((name.lower(), eachStructure))

    return strucutres
