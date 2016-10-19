#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\station\medical\cloneStation.py
import blue
import uicls
import uthread
import uicontrols
import uiprimitives
import localization
import carbonui.const as uiconst
from carbonui.uicore import uicorebase as uicore
from carbonui.util.color import Color
from eve.client.script.ui.structure import ChangeSignalConnect
from inventorycommon.util import IsWormholeRegion

class CloneStationWindow(uicontrols.Window):
    __guid__ = 'form.CloneStationWindow'
    __notifyevents__ = ['OnSessionChanged']
    default_width = 600
    default_height = 100
    default_windowID = 'CloneStationWindow'
    default_topParentHeight = 0
    default_clipChildren = True
    default_isPinable = False
    LINE_COLOR = (1, 1, 1, 0.2)
    BLUE_COLOR = (0.0, 0.54, 0.8, 1.0)
    GREEN_COLOR = (0.0, 1.0, 0.0, 0.8)
    GRAY_COLOR = Color.GRAY5
    PADDING = 15

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        self.medicalController = attributes.medicalController
        self.ChangeSignalConnection(connect=True)
        self.Layout()
        uthread.new(self.Reload)

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.medicalController.on_home_station_changed, self.OnHomeStationChanged)]
        ChangeSignalConnect(signalAndCallback, connect)

    def Layout(self):
        self.MakeUnMinimizable()
        self.HideHeader()
        self.MakeUnResizeable()
        self.container = uicontrols.ContainerAutoSize(parent=self.GetMainArea(), align=uiconst.TOTOP, alignMode=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, padding=(self.PADDING,
         self.PADDING,
         self.PADDING,
         self.PADDING), callback=self.OnContainerResized)
        uicontrols.EveLabelLargeBold(parent=self.container, align=uiconst.TOTOP, text=localization.GetByLabel('UI/Medical/Clone/HomeStation'))
        uicontrols.EveLabelMedium(parent=self.container, align=uiconst.TOTOP, text=localization.GetByLabel('UI/Medical/Clone/HomeStationDescription'), color=self.GRAY_COLOR, padding=(0, 0, 0, 15))
        uiprimitives.Line(parent=self.container, align=uiconst.TOTOP, color=self.LINE_COLOR)
        self.local = uicontrols.ContainerAutoSize(parent=self.container, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN)
        self.remoteTitle = uicontrols.EveLabelLargeBold(parent=self.container, align=uiconst.TOTOP, text=localization.GetByLabel('UI/Medical/Clone/CorporationOffices'), padding=(0, 15, 0, 0), state=uiconst.UI_DISABLED)
        self.remoteText = uicontrols.EveLabelMedium(parent=self.container, align=uiconst.TOTOP, text=localization.GetByLabel('UI/Medical/Clone/CorporationOfficesDescription'), color=self.GRAY_COLOR, padding=(0, 0, 0, 0), state=uiconst.UI_DISABLED)
        self.remoteTimer = uicontrols.EveLabelMedium(parent=self.container, align=uiconst.TOTOP, text='', color=self.GRAY_COLOR, padding=(0, 0, 0, 15), state=uiconst.UI_DISABLED)
        self.remote = uicls.ScrollContainer(parent=self.container, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN)
        self.closeButton = uicontrols.Button(parent=self.container, label=localization.GetByLabel('UI/Generic/Cancel'), func=self.Close, align=uiconst.TOTOP, fontsize=13, padding=(220, 10, 220, 0))
        uicore.animations.FadeTo(self.container, startVal=0.0, endVal=1.0, duration=0.5)

    def OnSessionChanged(self, *args):
        self.Close()

    def OnContainerResized(self):
        self.width = self.default_width
        self.height = self.container.height + self.PADDING * 2

    def Reload(self):
        if self.destroyed:
            return
        self.local.DisableAutoSize()
        self.local.Flush()
        self.remote.Flush()
        self.homeStationID = self.medicalController.GetHomeStation()
        stations, remoteStationDate = self.medicalController.GetPotentialHomeStations()
        hasRemote = bool(len([ s for s in stations if s.isRemote ]))
        showRemoteStations = self.medicalController.ShowRemoteStations()
        if showRemoteStations and hasRemote:
            self.remoteTitle.display = True
            self.remoteText.display = True
            self.remoteTimer.display = True
            if remoteStationDate and remoteStationDate > blue.os.GetWallclockTime():
                self.remote.state = uiconst.UI_DISABLED
                self.remote.opacity = 0.2
                self.remoteTimer.text = localization.GetByLabel('UI/Medical/Clone/NextRemoteChangeDate', nextDate=remoteStationDate)
            else:
                self.remote.state = uiconst.UI_PICKCHILDREN
                self.remote.opacity = 1.0
                self.remoteTimer.text = localization.GetByLabel('UI/Medical/Clone/NextRemoteChangeNow')
        else:
            self.remoteTitle.display = False
            self.remoteText.display = False
            self.remote.state = uiconst.UI_HIDDEN
            self.remoteTimer.display = False
        uiprimitives.Line(parent=self.remote, align=uiconst.TOTOP, color=self.LINE_COLOR)
        for station in stations:
            if not showRemoteStations and station.isRemote:
                continue
            self.AddStation(station.stationID, station.isRemote)

        if session.structureid is not None and not IsWormholeRegion(session.regionid):
            self.AddStructure(session.structureid)
        self.remote.height = min(self.remote.mainCont.height + 45, 305)
        self.local.EnableAutoSize()

    def AddStation(self, stationID, isRemote):
        station = cfg.stations.Get(stationID)
        stationTypeID = station.stationTypeID
        stationName = station.stationName
        self.AddCloneLocation(stationID, stationName, stationTypeID, isRemote, lambda *args: self.SetHome(stationID))

    def AddStructure(self, structureID):
        inv = sm.GetService('invCache').GetInventoryFromId(structureID)
        typeID = inv.GetItem().typeID
        locationName = cfg.evelocations.Get(structureID).locationName
        self.AddCloneLocation(structureID, locationName, typeID, False, lambda *args: self.SetHome(structureID))

    def SetHome(self, locationID):
        self.medicalController.SetHomeStation(locationID)

    def AddCloneLocation(self, stationID, stationName, stationTypeID, isRemote, func):
        if isRemote:
            if stationID == session.hqID:
                title = localization.GetByLabel('UI/Medical/Clone/CorporationHeadquarters')
            else:
                title = localization.GetByLabel('UI/Medical/Clone/CorporationOffice')
            parent = self.remote
            color = self.BLUE_COLOR
        else:
            if stationID in (session.stationid2, session.structureid):
                title = localization.GetByLabel('UI/Medical/Clone/ThisStation')
            else:
                title = localization.GetByLabel('UI/Medical/Clone/SchoolHeadquarters')
            parent = self.local
            color = self.GREEN_COLOR
        container = uicontrols.ContainerAutoSize(parent=parent, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, bgColor=(0.2, 0.2, 0.2, 0.3))
        container.DisableAutoSize()
        label = "<url=showinfo:%d//%d alt='%s'>%s</url>" % (stationTypeID,
         stationID,
         title,
         stationName)
        uicontrols.EveLabelMediumBold(parent=container, align=uiconst.TOTOP, text=title, padding=(7, 5, 0, 0), color=color)
        uicontrols.EveLabelMediumBold(parent=container, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, text=label, padding=(7, 0, 140, 5))
        if stationID != self.homeStationID:
            uicontrols.Button(parent=container, label=localization.GetByLabel('UI/Medical/Clone/SetHomeStationButton'), align=uiconst.CENTERRIGHT, fontsize=13, fixedwidth=140, fixedheight=30, pos=(5, 0, 0, 0), func=func)
        else:
            uicontrols.EveLabelMediumBold(parent=container, align=uiconst.CENTERRIGHT, text=localization.GetByLabel('UI/Medical/Clone/CurrentHomeStation'), padding=(-15, 0, 0, 0))
        uiprimitives.Line(parent=parent, align=uiconst.TOTOP, color=self.LINE_COLOR)
        container.EnableAutoSize()

    def OnHomeStationChanged(self):
        self.Close()

    def Close(self, *args, **kwargs):
        try:
            self.ChangeSignalConnection(connect=False)
        finally:
            uicontrols.Window.Close(self, *args, **kwargs)
