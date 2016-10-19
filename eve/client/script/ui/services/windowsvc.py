#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\windowsvc.py
from carbonui.primitives.base import ScaleDpi
from eve.client.script.ui.control.themeColored import FillThemeColored
import service
import uicontrols
from eve.client.script.ui.inflight.scannerFiles.moonScanner import MoonScanner
import uiutil
import form
import util
import carbonui.const as uiconst
import telemetry
from carbonui.uicore import uicorebase as uicore
from eve.client.script.ui.shared.systemMenu.betaOptions import IsBetaScannersEnabled
from eve.client.script.ui.structure.dockedOverlay.dockedPanel import DockedPanel
from eve.common.script.sys.eveCfg import IsDockedInStructure
import evegraphics.settings as gfxsettings

class WindowMgr(service.Service):
    __guid__ = 'svc.window'
    __servicename__ = 'window'
    __displayname__ = 'Window Service'
    __dependencies__ = ['form']
    __exportedcalls__ = {'CloseContainer': [],
     'OpenWindows': []}
    __notifyevents__ = ['DoSessionChanging',
     'OnSessionChanged',
     'ProcessRookieStateChange',
     'OnEndChangeDevice',
     'ProcessDeviceChange',
     'OnBlurredBufferCreated',
     'OnHideUI',
     'OnShowUI']
    __startupdependencies__ = ['settings']

    def Run(self, memStream = None):
        self.LogInfo('Starting Window Service')
        self.wndIntersectionsByRects = {}

    def Stop(self, memStream = None):
        self.LogInfo('Stopping Window Service')
        service.Service.Stop(self)

    def ProcessRookieStateChange(self, state):
        if sm.GetService('connection').IsConnected():
            self.OpenWindows()

    def ProcessDeviceChange(self, *args):
        self.PreDeviceChange_DesktopLayout = uicontrols.Window.GetDesktopWindowLayout()

    def OnEndChangeDevice(self, change, *args):
        if 'BackBufferHeight' in change or 'BackBufferWidth' in change:
            self.RealignWindows()
            sm.GetService('device').SetupUIScaling()

    def ValidateWindows(self):
        d = uicore.desktop
        all = uicore.registry.GetValidWindows(1, floatingOnly=True)
        for wnd in all:
            if wnd.align != uiconst.RELATIVE:
                continue
            wnd.left = max(-wnd.width + 64, min(d.width - 64, wnd.left))
            wnd.top = max(0, min(d.height - wnd.GetCollapsedHeight(), wnd.top))

    def DoSessionChanging(self, isRemote, session, change):
        if not eve.session.charid:
            for layer in (uicore.layer.starmap,):
                for each in layer.children:
                    each.Close()

    def OnSessionChanged(self, isRemote, session, change):
        if sm.GetService('connection').IsConnected() and self.IsLocationChange(change):
            self.OpenWindows()

    def IsLocationChange(self, change):
        if 'locationid' in change:
            return True
        if 'structureid' in change:
            return True
        if 'shipid' in change and session.structureid in change['shipid']:
            return True
        return False

    def OnHideUI(self, *args):
        self.UpdateIntersectionBackground()

    def OnShowUI(self, *args):
        self.UpdateIntersectionBackground()

    def ResetWindowSettings(self):
        closeStacks = []
        triggerUpdate = []
        for each in uicore.registry.GetWindows():
            if not isinstance(each, uicontrols.WindowCore):
                continue
            if each.isDialog:
                continue
            if each.parent != uicore.layer.main:
                uiutil.Transplant(each, uicore.layer.main)
            if isinstance(each, uicontrols.WindowStackCore):
                closeStacks.append(each)
            else:
                triggerUpdate.append(each)
                each.sr.stack = None
                each.state = uiconst.UI_HIDDEN
                each.align = uiconst.TOPLEFT
                each.ShowHeader()
                each.ShowBackground()

        for each in closeStacks:
            each.Close()

        uicontrols.Window.ResetAllWindowSettings()
        favorClasses = [form.LSCChannel,
         form.ActiveItem,
         form.OverView,
         form.DroneView,
         form.WatchListPanel]
        done = []
        for cls in favorClasses:
            for each in triggerUpdate:
                if each not in done and isinstance(each, cls):
                    each.InitializeSize()
                    each.InitializeStatesAndPosition()
                    done.append(each)

        for each in triggerUpdate:
            if each not in done:
                each.InitializeSize()
                each.InitializeStatesAndPosition()

        settings.user.ui.Delete('targetOrigin')
        sm.GetService('target').ArrangeTargets()

    def RealignWindows(self):
        desktopLayout = getattr(self, 'PreDeviceChange_DesktopLayout', None)
        if desktopLayout:
            uicontrols.Window.LoadDesktopWindowLayout(desktopLayout)
        self.PreDeviceChange_DesktopLayout = None
        sm.GetService('target').ArrangeTargets()

    @telemetry.ZONE_METHOD
    def OpenWindows(self):
        if not (eve.rookieState and eve.rookieState < 10):
            wndsToCheck = [util.KeyVal(cls=form.MailWindow, cmd=uicore.cmd.OpenMail),
             util.KeyVal(cls=form.Wallet, cmd=uicore.cmd.OpenWallet),
             util.KeyVal(cls=form.Corporation, cmd=uicore.cmd.OpenCorporationPanel),
             util.KeyVal(cls=form.AssetsWindow, cmd=uicore.cmd.OpenAssets),
             util.KeyVal(cls=form.Channels, cmd=uicore.cmd.OpenChannels),
             util.KeyVal(cls=form.Journal, cmd=uicore.cmd.OpenJournal),
             util.KeyVal(cls=form.Logger, cmd=uicore.cmd.OpenLog),
             util.KeyVal(cls=form.CharacterSheet, cmd=uicore.cmd.OpenCharactersheet),
             util.KeyVal(cls=form.AddressBook, cmd=uicore.cmd.OpenPeopleAndPlaces),
             util.KeyVal(cls=form.RegionalMarket, cmd=uicore.cmd.OpenMarket),
             util.KeyVal(cls=form.Notepad, cmd=uicore.cmd.OpenNotepad)]
            if session.stationid2:
                sm.GetService('gameui').ScopeCheck(['station', 'station_inflight'])
                wndsToCheck += [util.KeyVal(cls=form.Inventory, cmd=uicore.cmd.OpenInventory, windowID=('InventoryStation', None)), util.KeyVal(cls=form.StationItems, cmd=uicore.cmd.OpenHangarFloor), util.KeyVal(cls=form.StationShips, cmd=uicore.cmd.OpenShipHangar)]
                if session.corpid:
                    wnd = self._GetCorpDeliveriesWnd(invID=('StationCorpDeliveries', session.stationid2))
                    wndsToCheck.append(wnd)
                    office = sm.GetService('corp').GetOffice()
                    if office:
                        officeItemID = office.itemID
                        wnd = self._GetCorpHangarInvWnd(wndCls=form.StationCorpHangars, invID=('StationCorpHangars', officeItemID))
                        wndsToCheck.append(wnd)
                        wndsToCheck += self._GetCorpHangarDivisionInvWnds(invIdName='StationCorpHangar', locationID=officeItemID)
            elif session.structureid and session.structureid != session.shipid:
                sm.GetService('gameui').ScopeCheck(['station_inflight'])
                wndsToCheck += [util.KeyVal(cls=form.Inventory, cmd=uicore.cmd.OpenInventory, windowID=('InventoryStructure', None)), util.KeyVal(cls=form.Inventory, cmd=uicore.cmd.OpenHangarFloor, windowID=('StructureItemHangar', session.structureid)), util.KeyVal(cls=form.Inventory, cmd=uicore.cmd.OpenShipHangar, windowID=('StructureShipHangar', session.structureid))]
                if session.corpid:
                    wnd = self._GetCorpDeliveriesWnd(invID=('StationCorpDeliveries', session.structureid))
                    wndsToCheck.append(wnd)
                    if sm.GetService('structureOffices').HasOffice():
                        wnd = self._GetCorpHangarInvWnd(wndCls=form.Inventory, invID=('StructureCorpHangars', session.structureid))
                        wndsToCheck.append(wnd)
                        wndsToCheck += self._GetCorpHangarDivisionInvWnds(invIdName='StructureCorpHangar', locationID=session.structureid)
            elif session.solarsystemid and session.shipid:
                if IsBetaScannersEnabled():
                    from eve.client.script.ui.inflight.probeScannerWindow import ProbeScannerWindow
                    from eve.client.script.ui.inflight.scannerFiles.directionalScannerWindow import DirectionalScanner
                else:
                    from eve.client.script.ui.inflight.scanner import Scanner as ProbeScannerWindow
                    from eve.client.script.ui.inflight.scannerFiles.directionalScanner import DirectionalScanner
                sm.GetService('gameui').ScopeCheck(['inflight', 'station_inflight'])
                wndsToCheck += [util.KeyVal(cls=form.Inventory, cmd=uicore.cmd.OpenInventory, windowID=('InventorySpace', None)),
                 util.KeyVal(cls=ProbeScannerWindow, cmd=uicore.cmd.OpenScanner),
                 util.KeyVal(cls=DirectionalScanner, cmd=uicore.cmd.OpenDirectionalScanner),
                 util.KeyVal(cls=MoonScanner, cmd=MoonScanner.Open)]
            else:
                sm.GetService('gameui').ScopeCheck()
            try:
                uicore.cmd.openingWndsAutomatically = True
                for checkWnd in wndsToCheck:
                    try:
                        cls = checkWnd.cls
                        cmd = checkWnd.cmd
                        windowID = getattr(checkWnd, 'windowID', cls.default_windowID)
                        args = getattr(checkWnd, 'args', ())
                        stackID = cls.GetRegisteredOrDefaultStackID()
                        wnd = uicontrols.Window.GetIfOpen(windowID)
                        if type(windowID) == tuple:
                            windowID = windowID[0]
                        isOpen = uicore.registry.GetRegisteredWindowState(windowID, 'open', False)
                        isMinimized = uicore.registry.GetRegisteredWindowState(windowID, 'minimized', False)
                        if isOpen and (stackID or not isMinimized) and not wnd:
                            cmd(*args)
                    except Exception as e:
                        self.LogException('Failed at opening window')

            finally:
                uicore.cmd.openingWndsAutomatically = False

        from eve.client.script.ui.shared.dockedUI import ReloadLobbyWnd
        ReloadLobbyWnd()

    def _GetCorpDeliveriesWnd(self, invID):
        wnd = util.KeyVal(cls=form.StationCorpDeliveries, cmd=uicore.cmd.OpenCorpDeliveries, windowID=form.Inventory.GetWindowIDFromInvID(invID))
        return wnd

    def _GetCorpHangarInvWnd(self, wndCls, invID):
        wnd = util.KeyVal(cls=wndCls, cmd=uicore.cmd.OpenCorpHangar, windowID=form.Inventory.GetWindowIDFromInvID(invID))
        return wnd

    def _GetCorpHangarDivisionInvWnds(self, invIdName, locationID):
        wndsToCheck = []
        for i in xrange(7):
            invID = ('%s' % invIdName, locationID, i)
            wnd = util.KeyVal(cls=form.Inventory, cmd=self._OpenCorpHangarDivision, windowID=form.Inventory.GetWindowIDFromInvID(invID), args=(invID,))
            wndsToCheck.append(wnd)

        return wndsToCheck

    def _OpenCorpHangarDivision(self, invID):
        form.Inventory.OpenOrShow(invID=invID, usePrimary=False, toggle=False)

    def OnBlurredBufferCreated(self):
        self.UpdateIntersectionBackground()

    def GetWindowIntersectionRects(self):
        ret = set()
        wndRects = self.GetWindowRects()
        numWnds = len(wndRects)
        for i in xrange(numWnds):
            for j in xrange(i + 1, numWnds):
                wnd1 = wndRects[i]
                wnd2 = wndRects[j]
                if self.IsIntersecting(wnd1, wnd2):
                    ret.add(self.GetIntersection(wnd1, wnd2))

        return ret

    def UpdateIntersectionBackground(self):
        desktop = uicore.uilib.desktopBlurredBg
        if not desktop:
            return
        currRects = self.GetWindowIntersectionRects()
        toRemove = [ rect for rect in self.wndIntersectionsByRects.keys() if rect not in currRects ]
        for rect in toRemove:
            intersection = self.wndIntersectionsByRects.pop(rect)
            intersection.Close()

        toCreate = [ rect for rect in currRects if rect not in self.wndIntersectionsByRects ]
        for x1, y1, x2, y2 in toCreate:
            intersection = FillThemeColored(parent=desktop, pos=(x1,
             y1,
             x2 - x1,
             y2 - y1), align=uiconst.TOPLEFT, padding=1, opacity=0.5)
            self.wndIntersectionsByRects[x1, y1, x2, y2] = intersection

        desktop.UpdateAlignmentAsRoot()

    def IsIntersecting(self, wnd1, wnd2):
        l1, t1, r1, b1 = wnd1
        l2, t2, r2, b2 = wnd2
        hoverlaps = True
        voverlaps = True
        if l1 > r2 or r1 < l2:
            hoverlaps = False
        if t1 > b2 or b1 < t2:
            voverlaps = False
        return hoverlaps and voverlaps

    def GetIntersection(self, wnd1, wnd2):
        l1, t1, r1, b1 = wnd1
        l2, t2, r2, b2 = wnd2
        left = max(l1, l2)
        top = max(t1, t2)
        right = min(r1, r2)
        bottom = min(b1, b2)
        return (left,
         top,
         right,
         bottom)

    def GetWindowRects(self):
        windows = uicore.registry.GetValidWindows()
        ret = [ (wnd.displayX,
         wnd.displayY,
         wnd.displayX + wnd.displayWidth,
         wnd.displayY + wnd.displayHeight) for wnd in windows ]
        neocom = sm.GetService('neocom').neocom
        if neocom:
            l, t, w, h = neocom.GetAbsolute()
            ret.append((ScaleDpi(l),
             ScaleDpi(t),
             ScaleDpi(l + w),
             ScaleDpi(t + h)))
        return ret

    def CloseContainer(self, invID):
        self.LogInfo('WindowSvc.CloseContainer request for id:', invID)
        checkIDs = (('loot', invID),
         ('lootCargoContainer', invID),
         'shipCargo_%s' % invID,
         'drones_%s' % invID,
         'containerWindow_%s' % invID)
        for windowID in checkIDs:
            wnd = uicontrols.Window.GetIfOpen(windowID=windowID)
            if wnd:
                wnd.Close()
                self.LogInfo('  WindowSvc.CloseContainer closing:', windowID)

    def GetCameraLeftOffset(self, width, align = None, left = 0, *args):
        try:
            offsetUI = gfxsettings.Get(gfxsettings.UI_OFFSET_UI_WITH_CAMERA)
        except gfxsettings.UninitializedSettingsGroupError:
            offsetUI = False

        if not offsetUI:
            return 0
        offset = int(gfxsettings.Get(gfxsettings.UI_CAMERA_OFFSET))
        if not offset:
            return 0
        if align in [uiconst.CENTER, uiconst.CENTERTOP, uiconst.CENTERBOTTOM]:
            camerapush = int(offset / 100.0 * uicore.desktop.width / 3.0)
            allowedOffset = int((uicore.desktop.width - width) / 2) - 10
            if camerapush < 0:
                return max(camerapush, -allowedOffset - left)
            if camerapush > 0:
                return min(camerapush, allowedOffset + left)
        return 0
