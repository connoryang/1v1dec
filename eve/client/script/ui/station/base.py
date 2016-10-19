#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\station\base.py
from eve.client.script.ui.station import stationServiceConst
from eve.client.script.ui.station.undockQuestions import IsOkToUndockWithMissingCargo, IsOkToUndock
from eve.client.script.ui.station.assembleModularShip import AssembleShip
from eveSpaceObject import spaceobjanimation
import evetypes
from evegraphics.fsd.graphicIDs import GetSofFactionName
from inventorycommon.util import IsModularShip
import turretSet
import sys
import service
import uiprimitives
import uicontrols
import uix
import uiutil
import uthread
import blue
import log
import util
import uicls
import carbonui.const as uiconst
import localization
from reprocessing.ui.reprocessingWnd import ReprocessingWnd
from eve.client.script.ui.shared.dockedUI import ReloadLobbyWnd, GetLobbyClass

class StationSvc(service.Service):
    __guid__ = 'svc.station'
    __update_on_reload__ = 0
    __exportedcalls__ = {'GetGuests': [],
     'IsGuest': [],
     'Setup': [],
     'Exit': [],
     'GetSvc': [],
     'LoadSvc': [],
     'GiveHint': [],
     'ClearHint': [],
     'StopAllStationServices': [],
     'CleanUp': [],
     'SelectShipDlg': [],
     'GetServiceState': []}
    __dependencies__ = ['journal',
     'insurance',
     't3ShipSvc',
     'crimewatchSvc']
    __notifyevents__ = ['OnCharNowInStation',
     'OnCharNoLongerInStation',
     'OnStationOwnerChanged',
     'OnDogmaItemChange',
     'ProcessStationServiceItemChange',
     'ProcessSessionChange',
     'OnCharacterHandler',
     'OnDogmaAttributeChanged',
     'OnSessionChanged',
     'OnActiveShipModelChange',
     'OnStanceActive']

    def Run(self, memStream = None):
        self.LogInfo('Starting Station Service')
        self.CleanUp(clearGuestList=True)

    def OnSessionChanged(self, isRemote, session, change):
        if 'locationid' in change:
            oldLocation, newLocation = change['locationid']
            if util.IsStation(oldLocation):
                self.CleanUp(clearGuestList=True)

    def ProcessSessionChange(self, isRemote, session, change):
        if 'stationid' in change:
            oldStationID, newStationID = change['stationid']
            if newStationID:
                self.GetServiceStates(1)
            else:
                self.serviceItemsState = None

    def ProcessStationServiceItemChange(self, stationID, solarSystemID, serviceID, stationServiceItemID, isEnabled):
        self.GetServiceStates()
        if serviceID in self.serviceItemsState:
            state = self.serviceItemsState[serviceID]
            state.stationServiceItemID = stationServiceItemID
            state.isEnabled = isEnabled
        sm.ScatterEvent('OnProcessStationServiceItemChange', stationID, solarSystemID, serviceID, stationServiceItemID, isEnabled)

    def GetServiceStates(self, force = 0):
        if not self.serviceItemsState or force:
            if util.IsOutpost(eve.session.stationid) or sm.GetService('godma').GetType(eve.stationItem.stationTypeID).isPlayerOwnable == 1:
                self.serviceItemsState = sm.RemoteSvc('corpStationMgr').GetStationServiceStates()
            else:
                self.serviceItemsState = {}

    def GetServiceState(self, serviceID):
        self.GetServiceStates()
        return self.serviceItemsState.get(serviceID, None)

    def OnStationOwnerChanged(self, *args):
        uthread.pool('StationSvc::OnStationOwnerChanged --> LoadLobby', self.ReloadLobby)

    def OnCharNowInStation(self, rec):
        charID, corpID, allianceID, warFactionID = rec
        if charID not in self.guests:
            self.guests[charID] = (corpID, allianceID, warFactionID)
        self.serviceItemsState = None

    def OnCharNoLongerInStation(self, rec):
        charID, corpID, allianceID, factionID = rec
        if charID in self.guests:
            self.guests.pop(charID)
        self.serviceItemsState = None

    def GetGuests(self):
        if not self.guestListReceived:
            guests = sm.RemoteSvc('station').GetGuests()
            for charID, corpID, allianceID, warFactionID in guests:
                self.guests[charID] = (corpID, allianceID, warFactionID)

            self.guestListReceived = True
        return self.guests

    def IsGuest(self, whoID):
        if len(self.guests) == 0:
            self.GetGuests()
        return whoID in self.guests

    def Stop(self, memStream = None):
        self.LogInfo('Stopping Station Service')
        self.CleanUp(clearGuestList=True)

    def CheckSession(self, change):
        if util.GetActiveShip() != session.shipid:
            if eve.session.shipid:
                hangarInv = sm.GetService('invCache').GetInventory(const.containerHangar)
                hangarItems = hangarInv.List(const.flagHangar)
                for each in hangarItems:
                    if each.itemID == session.shipid:
                        self.activeShipItem = each
                        break

    def GetStation(self):
        self.station = sm.GetService('ui').GetStation(eve.session.stationid)

    def GetServiceDisplayName(self, service):
        s = self.GetStationServiceData(service)
        if s:
            return s.label
        return localization.GetByLabel('UI/Common/Unknown')

    def GetStationServiceData(self, serviceName):
        return stationServiceConst.serviceDataByNameID.get(serviceName, None)

    def CleanUp(self, storeCamera = 1, clearGuestList = False):
        try:
            if getattr(self, 'underlay', None):
                uicore.registry.UnregisterWindow(self.underlay)
                self.underlay.OnClick = None
                self.underlay.Minimize = None
                self.underlay.Maximize = None
        except:
            pass

        uix.Close(self, ['closeBtn',
         'hint',
         'underlay',
         'lobby'])
        self.lobby = None
        self.underlay = None
        self.closeBtn = None
        self.hint = None
        self.fittingflags = None
        self.selected_service = None
        self.loading = None
        self.active_service = None
        self.refreshingfitting = False
        self.activeShipItem = None
        self.activeShipTypeID = None
        self.activeshipmodel = None
        self.loadingSvc = 0
        self.exitingstation = 0
        self.activatingShip = 0
        self.leavingShip = 0
        self.paperdollState = None
        self.serviceItemsState = {}
        self.maxZoom = 750.0
        self.minZoom = 150.0
        self.station = None
        self.previewColorIDs = {'MAIN': 0,
         'MARKINGS': 0,
         'LIGHTS': 0}
        self.pastUndockPointOfNoReturn = False
        if clearGuestList:
            self.guests = {}
            self.guestListReceived = False

    def StopAllStationServices(self):
        for serviceData in stationServiceConst.serviceData:
            if sm.IsServiceRunning(serviceData.name):
                sm.services[serviceData.name].Stop()

    def Setup(self, reloading = 0):
        self.CleanUp(0)
        self.loading = 1
        if not reloading:
            eve.Message('OnEnterStation')
        if self.station is None and eve.session.stationid:
            self.station = sm.GetService('ui').GetStation(eve.session.stationid)
        sm.GetService('autoPilot').SetOff('toggled by Station Entry')
        if sm.GetService('viewState').IsViewActive('starmap', 'systemmap'):
            sm.StartService('map').MinimizeWindows()
        if sm.GetService('viewState').IsViewActive('planet'):
            sm.GetService('planetUI').MinimizeWindows()
        self.loading = 0
        self.sprite = None
        if not reloading:
            if util.GetActiveShip() is None:
                sm.GetService('tutorial').OpenTutorialSequence_Check(uix.cloningWhenPoddedTutorial)
            if sm.GetService('skills').GetSkillPoints() >= 1500000:
                sm.GetService('tutorial').OpenTutorialSequence_Check(uix.cloningTutorial)

    def GetPaperdollStateCache(self):
        if self.paperdollState is None:
            self.paperdollState = sm.RemoteSvc('charMgr').GetPaperdollState()
        return self.paperdollState

    def OnCharacterHandler(self):
        self.ClearPaperdollStateCache()

    def ClearPaperdollStateCache(self):
        self.paperdollState = None

    def BlinkButton(self, what):
        lobby = GetLobbyClass().GetIfOpen()
        if lobby:
            lobby.BlinkButton(what)

    def DoPOSWarning(self):
        if sm.GetService('godma').GetType(eve.stationItem.stationTypeID).isPlayerOwnable == 1:
            eve.Message('POStationWarning')

    def TryActivateShip(self, invitem, onSessionChanged = 0, secondTry = 0):
        shipid = invitem.itemID
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        if shipid == dogmaLocation.GetCurrentShipID():
            return
        if self.activatingShip:
            return
        dogmaLocation.CheckSkillRequirementsForType(None, invitem.typeID, 'ShipHasSkillPrerequisites')
        sm.GetService('invCache').TryLockItem(shipid, 'lockItemActivating', {'itemType': invitem.typeID}, 1)
        self.activatingShip = 1
        try:
            if IsModularShip(invitem.typeID):
                if eve.Message('AskActivateTech3Ship', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                    return
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
            dogmaLocation.MakeShipActive(shipid)
            self.activeShipItem = invitem
            if invitem.groupID != const.groupRookieship:
                sm.GetService('tutorial').OpenTutorialSequence_Check(uix.insuranceTutorial)
            sm.GetService('fleet').UpdateFleetInfo()
            sm.ScatterEvent('OnClient_ShipActivated')
        finally:
            self.activatingShip = 0
            sm.GetService('invCache').UnlockItem(shipid)

    def TryLeaveShip(self, invitem, onSessionChanged = 0, secondTry = 0):
        shipid = invitem.itemID
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        if shipid != dogmaLocation.GetCurrentShipID():
            return
        if self.leavingShip:
            return
        sm.GetService('invCache').TryLockItem(shipid, 'lockItemLeavingShip', {'itemType': invitem.typeID}, 1)
        self.leavingShip = 1
        try:
            shipsvc = sm.GetService('gameui').GetShipAccess()
            sm.GetService('gameui').KillCargoView(shipid)
            shipsvc.LeaveShip(shipid)
        finally:
            self.leavingShip = 0
            sm.GetService('invCache').UnlockItem(shipid)

    def GetTech3ShipFromSlimItem(self, slimItem):
        subSystemIds = {}
        for module in slimItem.modules:
            if module.categoryID == const.categorySubSystem:
                subSystemIds[module.groupID] = module.typeID

        if len(subSystemIds) < const.visibleSubSystems:
            AssembleShip.Open(windowID='AssembleShip', ship=slimItem, groupIDs=subSystemIds.keys())
            return
        return self.t3ShipSvc.GetTech3ShipFromDict(slimItem.typeID, subSystemIds)

    def OnDogmaItemChange(self, item, change):
        if session.stationid is None:
            return
        if item.groupID in const.turretModuleGroups:
            self.FitHardpoints()

    def OnActiveShipModelChange(self, model, shipItem):
        self.activeshipmodel = model
        self.activeShipTypeID = shipItem.typeID
        self.FitHardpoints()

    def OnStanceActive(self, shipID, stanceID):
        if util.GetActiveShip() == shipID:
            if self.activeshipmodel is not None:
                spaceobjanimation.SetShipAnimationStance(self.activeshipmodel, stanceID)

    def FitHardpoints(self):
        if not self.activeshipmodel or self.activeShipTypeID is None or self.refreshingfitting:
            return
        self.refreshingfitting = True
        activeShip = util.GetActiveShip()
        sofFactionName = GetSofFactionName(evetypes.GetGraphicID(self.activeShipTypeID))
        turretSet.TurretSet.FitTurrets(activeShip, self.activeshipmodel, sofFactionName)
        self.refreshingfitting = False

    def ModuleListFromGodmaSlimItem(self, slimItem):
        list = []
        for module in slimItem.modules:
            list.append((module.itemID, module.typeID))

        list.sort()
        return list

    def GetUnderlay(self):
        if self.underlay is None:
            for each in uicore.layer.main.children[:]:
                if each is not None and not each.destroyed and each.name == 'services':
                    uicore.registry.UnregisterWindow(each)
                    each.OnClick = None
                    each.Minimize = None
                    each.Maximize = None
                    each.Close()

            self.underlay = uiprimitives.Sprite(name='services', parent=uicore.layer.main, align=uiconst.TOTOP, state=uiconst.UI_HIDDEN)
            self.underlay.scope = 'station'
            self.underlay.minimized = 0
            self.underlay.Minimize = self.MinimizeUnderlay
            self.underlay.Maximize = self.MaximizeUnderlay
            main = uiprimitives.Container(name='mainparentXX', parent=self.underlay, align=uiconst.TOALL, pos=(0, 0, 0, 0))
            main.OnClick = self.ClickParent
            main.state = uiconst.UI_NORMAL
            sub = uiprimitives.Container(name='subparent', parent=main, align=uiconst.TOALL, pos=(0, 0, 0, 0))
            captionparent = uiprimitives.Container(name='captionparent', parent=main, align=uiconst.TOPLEFT, left=128, top=36, idx=0)
            caption = uicontrols.CaptionLabel(text='', parent=captionparent)
            self.closeBtn = uicontrols.ButtonGroup(btns=[[localization.GetByLabel('UI/Commands/CmdClose'),
              self.CloseSvc,
              None,
              81]], parent=sub)
            self.sr.underlay = uicontrols.WindowUnderlay(parent=main)
            self.sr.underlay.padding = (-1, -10, -1, 0)
            svcparent = uiprimitives.Container(name='serviceparent', parent=sub, align=uiconst.TOALL, pos=(0, 0, 0, 0))
            self.underlay.sr.main = main
            self.underlay.sr.svcparent = svcparent
            self.underlay.sr.caption = caption
            uicore.registry.RegisterWindow(self.underlay)
        return self.underlay

    def MinimizeUnderlay(self, *args):
        self.underlay.state = uiconst.UI_HIDDEN

    def MaximizeUnderlay(self, *args):
        self.underlay.state = uiconst.UI_PICKCHILDREN
        self.ClickParent()

    def ClickParent(self, *args):
        for each in uicore.layer.main.children:
            if getattr(each, 'isDockWnd', 0) == 1 and each.state == uiconst.UI_NORMAL:
                uiutil.SetOrder(each, -1)

    def LoadSvc(self, service, close = 1):
        serviceInfo = self.GetStationServiceData(service)
        if service is not None and serviceInfo is not None:
            self.ExecuteCommand(serviceInfo.command)
            return
        if getattr(self, 'loadingSvc', 0):
            return
        self.loadingSvc = 1
        while self.loading:
            blue.pyos.synchro.SleepWallclock(500)

        if self.selected_service is None:
            if service:
                self._LoadSvc(1, service)
        elif service == self.selected_service:
            if close:
                self._LoadSvc(0)
        else:
            self._LoadSvc(0, service)
        self.loadingSvc = 0

    def ExecuteCommand(self, cmdstr):
        func = getattr(uicore.cmd, cmdstr, None)
        if func:
            func()

    def GetSvc(self, svcname = None):
        if self.active_service is not None:
            if svcname is not None:
                if self.selected_service == svcname:
                    return self.active_service
            else:
                return self.active_service

    def ReloadLobby(self):
        ReloadLobbyWnd()

    def _LoadSvc(self, inout, service = None):
        self.loading = 1
        wnd = self.GetUnderlay()
        newsvc = None
        if inout == 1 and wnd is not None:
            self.ClearHint()
            newsvc, svctype = self.SetupService(wnd, service)
        if wnd.absoluteRight - wnd.absoluteLeft < 700 and inout == 1:
            sm.GetService('neocom').Minimize()
        height = uicore.desktop.height - 180
        wnd.state = uiconst.UI_PICKCHILDREN
        if inout == 1:
            sm.GetService('neocom').SetLocationInfoState(0)
        wnd.height = height
        if inout:
            wnd.top = -height
        uicore.effect.MorphUI(wnd, 'top', [-height, 0][inout], 500.0, 1, 1)
        snd = service
        if inout == 0:
            snd = self.selected_service
        if snd is not None:
            eve.Message('LoadSvc_%s%s' % (snd, ['Out', 'In'][inout]))
        blue.pyos.synchro.SleepWallclock([750, 1250][inout])
        if inout == 0:
            sm.GetService('neocom').SetLocationInfoState(1)
        if newsvc is not None:
            if svctype == 'form':
                newsvc.Startup(self)
            elif settings.user.ui.Get('nottry', 0):
                newsvc.Initialize(wnd.sr.svcparent)
            else:
                try:
                    newsvc.Initialize(wnd.sr.svcparent)
                except:
                    log.LogException(channel=self.__guid__)
                    sys.exc_clear()

            self.active_service = newsvc
            self.selected_service = service
        else:
            uix.Flush(wnd.sr.svcparent)
            if self.active_service and hasattr(self.active_service, 'Reset'):
                self.active_service.Reset()
            self.active_service = None
            self.selected_service = service
        self.loading = 0
        if inout == 0 and service is not None:
            self._LoadSvc(1, service)
        if inout == 0 and service is None:
            uix.Flush(wnd.sr.svcparent)

    def Startup(self, svc):
        uthread.new(svc.Startup, self)

    def GiveHint(self, hintstr, left = 80, top = 320, width = 300):
        self.ClearHint()
        if self.hint is None:
            par = uiprimitives.Container(name='captionParent', parent=self.GetUnderlay().sr.main, align=uiconst.TOPLEFT, top=top, left=left, width=width, height=256, idx=0)
            self.hint = uicontrols.CaptionLabel(text='', parent=par, align=uiconst.TOALL, left=0, top=0)
        self.hint.parent.top = top
        self.hint.parent.left = left
        self.hint.parent.width = width
        self.hint.text = hintstr or ''

    def ClearHint(self):
        if self.hint is not None:
            self.hint.text = ''

    def SetupService(self, wnd, servicename):
        uix.Flush(wnd.sr.svcparent)
        svc = None
        topheight = 128
        btmheight = 0
        icon = 'ui_9_64_14'
        sz = 128
        top = -16
        icon = uicontrols.Icon(icon=icon, parent=wnd.sr.svcparent, left=0, top=top, size=sz, idx=0)
        iconpar = uiprimitives.Container(name='iconpar', parent=wnd.sr.svcparent, align=uiconst.TOTOP, height=96, clipChildren=1, state=uiconst.UI_PICKCHILDREN)
        bigicon = icon.CopyTo()
        bigicon.width = bigicon.height = sz * 2
        bigicon.top = -64
        bigicon.color.a = 0.1
        iconpar.children.append(bigicon)
        closeX = uicontrols.Icon(icon='ui_38_16_220')
        closeX.align = uiconst.TOPRIGHT
        closeX.left = closeX.top = 2
        closeX.OnClick = self.CloseSvc
        iconpar.children.append(closeX)
        line = uiprimitives.Line(parent=iconpar, align=uiconst.TOPRIGHT, height=1, left=2, top=16, width=18)
        icon.state = uiconst.UI_DISABLED
        wnd.sr.caption.text = self.GetServiceDisplayName(servicename)
        wnd.sr.caption.state = uiconst.UI_DISABLED
        return (svc, 'service')

    def CloseSvc(self, *args):
        uthread.new(self.LoadSvc, None)

    def PastUndockPointOfNoReturn(self):
        return getattr(self, 'pastUndockPointOfNoReturn', False)

    def AbortUndock(self, *args):
        self.exitingstation = 0
        self.pastUndockPointOfNoReturn = False
        self.ReloadLobby()
        sm.GetService('tutorial').UnhideTutorialWindow()
        viewSvc = sm.GetService('viewState')
        currentView = viewSvc.GetCurrentView()
        if currentView.name == 'hangar':
            currentView.StopExitAnimation()
            currentView.StopExitAudio()

    def Exit(self, *args):
        if self.exitingstation:
            self.AbortUndock()
            return False
        viewSvc = sm.GetService('viewState')
        currentView = viewSvc.GetCurrentView()
        if currentView.name == 'hangar':
            currentView.StartExitAnimation()
            currentView.StartExitAudio()
        if sm.GetService('actionObjectClientSvc').IsEntityUsingActionObject(session.charid):
            sm.GetService('actionObjectClientSvc').ExitActionObject(session.charid)
        if not IsOkToUndock(eve.stationItem.stationTypeID):
            return False
        shipID = util.GetActiveShip()
        if shipID is None:
            shipID = self.ShipPicker()
            if shipID is None:
                eve.Message('NeedShipToUndock')
                return False
            sm.GetService('clientDogmaIM').GetDogmaLocation().MakeShipActive(shipID)
        if not IsOkToUndockWithMissingCargo():
            return False
        self.exitingstation = 1
        uthread.new(self.LoadSvc, None)
        uthread.new(self.Undock_Thread, shipID)
        return True

    def Undock_Thread(self, shipID):
        if not self.exitingstation:
            lobby = GetLobbyClass().GetIfOpen()
            if lobby and not lobby.destroyed:
                lobby.SetUndockProgress(None)
            return
        undockSteps = 3
        undockDelay = 5000
        if session and session.nextSessionChange:
            duration = session.nextSessionChange - blue.os.GetSimTime()
            if duration > 0:
                undockDelay = max(undockDelay, (duration / const.SEC + 1) * 1000)
        for i in xrange(undockSteps):
            lobby = GetLobbyClass().GetIfOpen()
            if lobby and not lobby.destroyed:
                lobby.SetUndockProgress(i * 1.0 / undockSteps)
            blue.synchro.SleepSim(undockDelay / undockSteps)
            if not self.exitingstation:
                if lobby and not lobby.destroyed:
                    lobby.SetUndockProgress(None)
                return

        lobby = GetLobbyClass().GetIfOpen()
        if lobby and not lobby.destroyed:
            lobby.SetUndockProgress(1)
        self.pastUndockPointOfNoReturn = True
        self.UndockAttempt(shipID)

    def UndockAttempt(self, shipID):
        systemCheckSupressed = settings.user.suppress.Get('suppress.FacWarWarningUndock', None) == uiconst.ID_OK
        if not systemCheckSupressed and eve.session.warfactionid:
            isSafe = sm.StartService('facwar').CheckForSafeSystem(eve.stationItem, eve.session.warfactionid)
            if not isSafe:
                if not eve.Message('FacWarWarningUndock', {}, uiconst.OKCANCEL) == uiconst.ID_OK:
                    settings.user.suppress.Set('suppress.FacWarWarningUndock', None)
                    self.exitingstation = 0
                    self.AbortUndock()
                    return
        self.DoUndockAttempt(False, True, shipID)

    def DoUndockAttempt(self, ignoreContraband, observedSuppressed, shipID):
        try:
            shipsvc = sm.GetService('gameui').GetShipAccess()
            undockingLogLabel = localization.GetByLabel('UI/Station/UndockingFromStationToSystem', fromStation=eve.session.stationid2, toSystem=eve.session.solarsystemid2)
            sm.GetService('logger').AddText(undockingLogLabel)
            if observedSuppressed:
                ignoreContraband = settings.user.suppress.Get('suppress.ShipContrabandWarningUndock', None) == uiconst.ID_OK
            onlineModules = sm.GetService('clientDogmaIM').GetDogmaLocation().GetOnlineModules(shipID)
            try:
                sm.GetService('space').PrioritizeLoadingForIDs([session.stationid])
                sm.GetService('sessionMgr').PerformSessionChange('undock', shipsvc.Undock, shipID, ignoreContraband, onlineModules=onlineModules)
            except UserError as e:
                if e.msg == 'ShipNotInHangar':
                    capsuleID = e.dict.get('capsuleID', None)
                    dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
                    if capsuleID is not None:
                        dogmaLocation.MakeShipActive(capsuleID)
                    raise
                elif e.msg == 'ShipContrabandWarningUndock':
                    if eve.Message(e.msg, e.dict, uiconst.OKCANCEL, suppress=uiconst.ID_OK) == uiconst.ID_OK:
                        sys.exc_clear()
                        self.DoUndockAttempt(True, False, shipID)
                        return
                    else:
                        self.AbortUndock()
                        return
                else:
                    self.AbortUndock()
                    raise

            self.CloseStationWindows()
        except Exception as e:
            self.AbortUndock()
            raise

        self.exitingstation = 0
        self.hangarScene = None

    def CloseStationWindows(self):
        ReprocessingWnd.CloseIfOpen()

    def ShipPicker(self):
        hangarInv = sm.GetService('invCache').GetInventory(const.containerHangar)
        items = hangarInv.List(const.flagHangar)
        tmplst = []
        for item in items:
            if item[const.ixCategoryID] == const.categoryShip and item[const.ixSingleton]:
                tmplst.append((evetypes.GetName(item[const.ixTypeID]), item[const.ixItemID], item[const.ixTypeID]))

        ret = uix.ListWnd(tmplst, 'item', localization.GetByLabel('UI/Station/SelectShip'), None, 1)
        if ret is None:
            return
        return ret[1]

    def SelectShipDlg(self):
        hangarInv = sm.GetService('invCache').GetInventory(const.containerHangar)
        items = hangarInv.List(const.flagHangar)
        tmplst = []
        activeShipID = util.GetActiveShip()
        for item in items:
            if item[const.ixCategoryID] == const.categoryShip and item[const.ixSingleton]:
                tmplst.append((evetypes.GetName(item[const.ixTypeID]), item, item[const.ixTypeID]))

        if not tmplst:
            self.exitingstation = 0
            eve.Message('NeedShipToUndock')
            return
        ret = uix.ListWnd(tmplst, 'item', localization.GetByLabel('UI/Station/SelectShip'), None, 1)
        if ret is None or ret[1].itemID == activeShipID:
            self.exitingstation = 0
            return
        newActiveShip = ret[1]
        try:
            self.TryActivateShip(newActiveShip)
        except:
            self.exitingstation = 0
            raise

    def ChangeColorOfActiveShip(self, typeName, colorID, typeID):
        self.previewColorIDs[typeName] = colorID
        self.t3ShipSvc.ChangeColor(self.activeshipmodel, self.previewColorIDs, typeID)

    def ConfirmChangeColor(self):
        if self.previewColorIDs is None:
            return
        sm.GetService('invCache').GetInventoryFromId(util.GetActiveShip()).ChangeColor(self.previewColorIDs)
        eve.Message('ColorOfShipHasBeenChanged')

    def OnDogmaAttributeChanged(self, shipID, itemID, attributeID, value):
        if self.activeshipmodel and attributeID == const.attributeIsOnline and shipID == util.GetActiveShip():
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
            slot = None
            if not dogmaLocation.IsItemLoaded(shipID):
                dogmaLocation.LoadItem(shipID)
            if dogmaLocation.IsItemLoading(shipID):
                dogmaLocation.loadingItems[shipID].receive()
            for module in dogmaLocation.GetDogmaItem(shipID).GetFittedItems().itervalues():
                if module.itemID != itemID:
                    continue
                slot = module.flagID - const.flagHiSlot0 + 1
                sceneShip = self.activeshipmodel
                for turretSet in sceneShip.turretSets:
                    if turretSet.slotNumber == slot:
                        if module.IsOnline():
                            turretSet.EnterStateIdle()
                        else:
                            turretSet.EnterStateDeactive()


class StationLayer(uicls.LayerCore):
    __guid__ = 'form.StationLayer'

    def OnCloseView(self):
        sm.GetService('station').CleanUp()

    def OnOpenView(self):
        pass
