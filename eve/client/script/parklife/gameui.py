#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\parklife\gameui.py
from eve.client.script.ui.mouseInputHandler import MouseInputHandler
from eve.client.script.ui.shared.languageWindow import LanguageWindow
from logmodule import LogException
import uiprimitives
import carbonui.const as uiconst
import uiutil
from carbonui.control.menu import ClearMenuLayer
from eve.client.script.ui.control.resourceLoadingIndicator import ResourceLoadingIndicator
from eve.client.script.ui.tutorial.tutorialOverlay import TutorialOverlay
import everesourceprefetch
import uthread
import blue
import bluepy
import telemetry
import form
import log
import moniker
import trinity
import sys
import service
import antiaddiction
import urllib2
import audioConst
import const
import ccUtil
import viewstate
from eve.client.script.ui.podGuide.megaMenuManager import MegaMenuManager
from eve.client.script.ui.view.viewStateConfig import SetupViewStates
from eve.client.script.ui.view.viewStateConst import ViewState
from sceneManagerConsts import SCENE_TYPE_SPACE
from service import SERVICE_RUNNING
from gpcs import TRANSPORT_CLOSED_MESSAGES
import localization
import uicls
import login
import util
from evespacescene.playerdeath import PlayerDeathHandler
from evespacescene.routevisualizer import RouteVisualizer
from evespacescene.supernova import Supernova
import evegraphics.settings as gfxsettings
from eve.client.script.ui.shared.canNotStartTrainingWindow import CanNotStartTrainingClass
from eve.client.script.ui.services.eveFont import EveFontHandler
import carbon.client.script.sys.appUtils as appUtils
import gatekeeper
import everesourceprefetch
from eve.client.script.ui.util.disconnectNotice import DisconnectNotice
CUSTOM_MESSAGE_BOXES = {'UserAlreadyHasSkillInTraining': CanNotStartTrainingClass}
AFK_SECONDS = 10 * 60

class GameUI(service.Service):
    __guid__ = 'svc.gameui'
    __exportedcalls__ = {'StartupUI': [],
     'MessageBox': [],
     'Say': [],
     'GetShipAccess': [],
     'GetEntityAccess': [],
     'GetCurrentScope': []}
    __startupdependencies__ = ['device', 'settings', 'viewState']
    __dependencies__ = ['michelle',
     'machoNet',
     'inv',
     'neocom',
     'infoPanel',
     'shipTreeUI']
    __notifyevents__ = ['OnConnectionRefused',
     'OnDisconnect',
     'OnServerMessage',
     'OnRemoteMessage',
     'DoSessionChanging',
     'ProcessSessionChange',
     'OnSessionChanged',
     'DoBallsAdded',
     'DoBallClear',
     'OnNewState',
     'OnClusterShutdownInitiated',
     'OnClusterShutdownCancelled',
     'OnJumpQueueMessage',
     'ProcessActiveShipChanged',
     'OnViewStateChanged',
     'OnSetDevice',
     'OnShowMarketDetails',
     'OnShowContract',
     'OnShowOwnerDetailsWindow',
     'OnCreateNewMailWindow']

    def Run(self, ms):
        service.Service.Run(self, ms)
        self.wannaBeEgo = -1
        self.languages = None
        self.shutdownTime = None
        self.currentScope = []
        self.isAFK = False
        self.numSecondsAway = 0
        self.sceneManager = sm.GetService('sceneManager')
        self.playerDeathHandler = PlayerDeathHandler(self.sceneManager)
        self.routeVisualizer = RouteVisualizer()
        self.supernova = Supernova()
        if session.languageID == 'ZH':
            uicore.fontSizeFactor = 1.2
        audioConst.BTNCLICK_DEFAULT = 'click'
        defaults = {'debug': 0,
         'port': sm.services['machoNet'].defaultProxyPortOffset,
         'newbie': 1,
         'inputhost': 'localhost',
         'digit': ',',
         'decimal': '.',
         'eulaagreed': 0,
         'host': 0}
        for k, v in defaults.items():
            if not prefs.HasKey(k):
                prefs.SetValue(k, v)

        self.uiLayerList = [('l_hint', None, None),
         ('l_dragging', None, None),
         ('l_menu', None, None),
         ('l_mloading', None, None),
         ('l_modal', None, [('l_loadingFill', None, None), ('l_systemmenu', form.SystemMenu, None)]),
         ('l_utilmenu', None, None),
         ('l_tutorialOverlay', TutorialOverlay, None),
         ('l_alwaysvisible', None, None),
         ('l_abovemain', None, None),
         ('l_loading', None, None),
         ('l_main', None, None),
         ('l_infoBubble', None, None),
         ('l_viewstate', None, None)]
        self.shipAccess = None
        self.state = SERVICE_RUNNING
        uthread.worker('gameui::ShutdownTimer', self.__ShutdownTimer)
        uthread.worker('gameui::SessionTimeoutTimer', self.__SessionTimeoutTimer)
        uthread.worker('gameui::AFKTimer', self.__AFKTimer)
        uthread.new(self._UpdateCrashKeyValues).context = 'gameui::_UpdateCrashKeyValues'

    def _UpdateCrashKeyValues(self):
        self.LogInfo('UpdateCrashKeyValues loop starting')
        stats = []
        try:
            serverInfo = login.GetServerInfo()
            blue.SetCrashKeyValues(u'serverName', unicode(serverInfo.name))
            blue.SetCrashKeyValues(u'serverIP', unicode(serverInfo.IP))
        except:
            log.LogException()

        statNames = ['Blue/Memory/Malloc',
         'Blue/Memory/Python',
         'Blue/Memory/PageFileUsage',
         'Blue/Memory/WorkingSet']
        for each in statNames:
            s = blue.statistics.Find(each)
            if s:
                stats.append(s)

        while self.state == SERVICE_RUNNING:
            for each in stats:
                blue.SetCrashKeyValues(unicode(each.name), unicode(each.value))

            blue.SetCrashKeyValues(u'Trinity_shader_model', unicode(trinity.GetShaderModel()))
            blue.synchro.SleepWallclock(5000)

    def GetShipAccess(self):
        if self.shipAccess is not None:
            shipAccess, locationID, shipID, charID = self.shipAccess
            if locationID != eve.session.solarsystemid or eve.session.stationid:
                self.shipAccess = None
            elif shipID != eve.session.shipid:
                self.shipAccess = None
            elif charID != eve.session.charid:
                self.shipAccess = None
        if self.shipAccess is None:
            self.shipAccess = [moniker.GetShipAccess(),
             eve.session.solarsystemid or eve.session.stationid,
             eve.session.shipid,
             eve.session.charid]
        return self.shipAccess[0]

    def GetEntityAccess(self):
        return moniker.GetEntityAccess()

    def OnDisconnect(self, reason = 0, msg = ''):
        disconnectNotice = DisconnectNotice(logProvider=self)
        disconnectNotice.OnDisconnect(reason, msg)

    def OnConnectionRefused(self):
        sm.GetService('loading').CleanUp()

    def OnServerMessage(self, msg):
        uthread.new(self.OnServerMessage_thread, msg).context = 'gameui.ServerMessage'

    def OnServerMessage_thread(self, msg):
        if isinstance(msg, tuple) and len(msg) == 2:
            label, kwargs = msg
            msg = localization.GetByLabel(label, **kwargs)
        eve.Message('ServerMessage', {'msg': msg})

    def OnClusterShutdownInitiated(self, explanationLabel, when, duration):
        self.shutdownTime = when

    def OnJumpQueueMessage(self, msg, ready):
        self.Say(msg)

    def OnClusterShutdownCancelled(self, explanationLabel):
        self.shutdownTime = None

    def __ShutdownTimer(self):
        while self.state == SERVICE_RUNNING:
            try:
                if self.shutdownTime and self.shutdownTime - blue.os.GetWallclockTime() < 5 * const.MIN:
                    timeLeft = max(0L, self.shutdownTime - blue.os.GetWallclockTime())
                    self.Say(localization.GetByLabel('UI/Shared/ClusterShutdownInSeconds', timeLeft=timeLeft))
            except:
                log.LogException()
                sys.exc_clear()

            blue.pyos.synchro.SleepWallclock(5000)

    def __SessionTimeoutTimer(self):
        while self.state == SERVICE_RUNNING:
            try:
                if eve.session.maxSessionTime and eve.session.maxSessionTime - blue.os.GetWallclockTime() < 15 * const.MIN:
                    self.Say(localization.GetByLabel('UI/Shared/MaxSessionTimeExpiring', timeLeft=eve.session.maxSessionTime - blue.os.GetWallclockTime()))
            except:
                log.LogException()
                sys.exc_clear()

            blue.pyos.synchro.SleepWallclock(5000)

    def __AFKTimer(self):
        while self.state == SERVICE_RUNNING:
            try:
                if session.charid:
                    self.__CheckForAFK()
            except:
                log.LogException()
                sys.exc_clear()

            blue.pyos.synchro.SleepWallclock(1000)

    def __CheckForAFK(self):
        t = uicore.uilib.GetLastAppEventTime()
        if not t:
            return
        diffInSeconds = (blue.os.GetWallclockTime() - t) / const.SEC
        if not self.isAFK and diffInSeconds > AFK_SECONDS:
            self.LogNotice('I am now AFK after being idle for', diffInSeconds, 'seconds.')
            self.isAFK = True
            sm.RemoteSvc('charMgr').SetActivityStatus(const.PLAYER_STATUS_AFK, diffInSeconds)
        elif self.isAFK and diffInSeconds < AFK_SECONDS:
            self.LogNotice('I am no longer AFK after being idle for', self.numSecondsAway, 'seconds.')
            self.isAFK = False
            sm.RemoteSvc('charMgr').SetActivityStatus(const.PLAYER_STATUS_ACTIVE, self.numSecondsAway)
        self.numSecondsAway = diffInSeconds

    def OnRemoteMessage(self, msgID, dict = None, kw = None):
        if kw is None:
            kw = {}
        remoteNotifyMessages = ('SelfDestructInitiatedOther', 'SelfDestructImmediateOther', 'SelfDestructAbortedOther2')
        if msgID in remoteNotifyMessages and not settings.user.ui.Get('notifyMessagesEnabled', 1):
            return
        uthread.new(eve.Message, msgID, dict, **kw).context = 'gameui.ServerMessage'

    def TransitionCleanup(self, session, change):
        ClearMenuLayer()
        uicore.layer.utilmenu.Flush()
        for each in uicore.registry.GetWindows()[:]:
            if each.name.startswith('infowindow') and 'shipid' in change and each.sr.itemID in change['shipid']:
                each.Close()

    def ClearCacheFiles(self):
        if eve.Message('AskClearCacheReboot', {}, uiconst.YESNO) == uiconst.ID_YES:
            prefs.clearcache = 1
            appUtils.Reboot('clear cache')

    def ClearSettings(self):
        if eve.Message('AskClearSettingsReboot', {}, uiconst.YESNO) == uiconst.ID_YES:
            prefs.resetsettings = 1
            appUtils.Reboot('clear settings')

    def Stop(self, ms = None):
        service.Service.Stop(self, ms)

    @telemetry.ZONE_METHOD
    def ProcessSessionChange(self, isRemote, session, change, cheat = 0):
        if 'shipid' in change and change['shipid'][0] and not session.stationid2:
            sm.GetService('invCache').CloseContainer(change['shipid'][0])
        self.settings.SaveSettings()
        self.LogInfo('ProcessSessionChange: ', change, ',', session)
        if not isRemote:
            return

    def DoSessionChanging(self, isRemote, session, change):
        wasPodded, changedToStationFromSpace, changedToStructureFromSpace = self._WasCharacterPodded(change)
        if wasPodded:
            if changedToStationFromSpace:
                view = self._GetStationView()
            else:
                view = ViewState.Hangar
            viewState = sm.GetService('viewState')
            viewState.SetTransitionReason(viewState.GetCurrentViewInfo().name, view, 'clone')
        self.TransitionCleanup(session, change)
        if 'charid' in change and change['charid'][0] or 'userid' in change and change['userid'][0]:
            self.shipAccess = None

    def _WasCharacterPodded(self, change):
        shipIdChangedToNone = 'shipid' in change and change['shipid'][1] is None
        changedToStationFromSpace = 'stationid' in change and change['stationid'][0] is None and 'structureid' not in change
        changedToStructureFromSpace = 'structureid' in change and change['structureid'][0] is None and 'stationid' not in change
        wasPodded = (changedToStationFromSpace or changedToStructureFromSpace) and shipIdChangedToNone
        return (wasPodded, changedToStationFromSpace, changedToStructureFromSpace)

    def OnSetDevice(self, *args):
        uicore.layer.utilmenu.Flush()

    def OnViewStateChanged(self, oldView, newView):
        uicore.layer.utilmenu.Flush()

    def AnythingImportantInChange(self, change):
        ignoreKeys = ('fleetid', 'wingid', 'squadid', 'fleetrole', 'languageID')
        ck = change.keys()
        for k in ignoreKeys:
            try:
                ck.remove(k)
            except ValueError:
                pass

        return bool(ck)

    @telemetry.ZONE_METHOD
    def OnSessionChanged(self, isRemote, session, change):
        if not self.AnythingImportantInChange(change):
            return
        relevantSessionAttributes = ('userid', 'charid', 'solarsystemid', 'stationid', 'structureid', 'shipid', 'worldspaceid')
        changeIsRelevant = False
        for attribute in relevantSessionAttributes:
            if attribute in change:
                changeIsRelevant = True
                break

        if not changeIsRelevant:
            return
        if 'userid' in change:
            sm.GetService('uiColor').LoadUIColors()
            sm.GetService('tactical')
            uicore.mouseInputHandler = MouseInputHandler()
        if 'charid' in change:
            self.DoWindowIdentification()
            uthread.new(self.TryOpenLanguageWindow)
        if 'userid' in change or 'charid' in change:
            self.settings.LoadSettings()
            self.AlterDefaultSettings()
            gfx = gfxsettings.GraphicsSettings.GetGlobal()
            gfx.InitializeSettingsGroup(gfxsettings.SETTINGS_GROUP_UI, settings.user.ui)
            self.device.ApplyTrinityUserSettings()
        if 'shipid' in change and session.sessionChangeReason == 'selfdestruct':
            session.sessionChangeReason = 'board'
        if session.charid is None:
            self._HandleUserLogonSessionChange(isRemote, session, change, self.viewState)
        elif session.stationid is not None:
            self._HandleSessionChangeInStation(isRemote, session, change, self.viewState)
        elif session.structureid is not None:
            self._HandleSessionChangeInStructure(isRemote, session, change, self.viewState)
        elif session.worldspaceid is not None:
            self._HandleSessionChangeInWorldSpace(isRemote, session, change, self.viewState)
        elif session.solarsystemid is not None:
            self._HandleSessionChangeInSpace(isRemote, session, change, self.viewState)
        else:
            self.LogWarn('GameUI::OnSessionChanged, Lame Teardown of the client, it should get propper OnDisconnect event', isRemote, session, change)
            self.ScopeCheck()

    def AlterDefaultSettings(self):
        newbieAccount = session.role & service.ROLE_NEWBIE
        if newbieAccount:
            untouched = -1
            if settings.char.windows.Get('dockshipsanditems', untouched) == untouched and not settings.char.windows.Get('dockshipsanditems_altered', 0):
                settings.char.windows.Set('dockshipsanditems', 1)
                settings.char.windows.Set('dockshipsanditems_altered', 1)

    def _HandleUserLogonSessionChange(self, isRemote, session, change, viewSvc):
        antiaddiction.OnLogin()
        self.LogNotice('GameUI::OnSessionChanged, Heading for character selection', isRemote, session, change)
        if sm.GetService('webtools').GetVars():
            return
        if settings.public.generic.Get('showintro2', None) is None:
            settings.public.generic.Set('showintro2', prefs.GetValue('showintro2', 1))
        if not gatekeeper.user.IsInitialized():
            gatekeeper.user.Initialize(lambda args: sm.RemoteSvc('charUnboundMgr').GetCohortsForUser)
            experimentSvc = sm.StartService('experimentClientSvc')
            experimentSvc.OnUserLogon(languageID=session.languageID)
        else:
            self.LogWarn('GameUI::_HandleUserLogonSessionChange, running multiple times')
        if settings.public.generic.Get('showintro2', 1):
            uthread.pool('GameUI::ActivateView::intro', viewSvc.ActivateView, 'intro')
        else:
            characters = sm.GetService('cc').GetCharactersToSelect(False)
            if characters:
                uthread.pool('GameUI::ActivateView::charsel', viewSvc.ActivateView, 'charsel')
            else:
                uthread.pool('GameUI::GoCharacterCreation', self.GoCharacterCreation)

    def _GetStationView(self):
        return settings.user.ui.Get('defaultDockingView', ViewState.Hangar)

    def _GetStructureView(self):
        return settings.user.ui.Get('defaultStructureView', ViewState.Hangar)

    def _GetActivateViewFunction(self, viewSvc):
        activateViewFunc = None
        if viewSvc.IsViewActive('charactercreation'):
            activateViewFunc = viewSvc.ActivateView
        else:
            activateViewFunc = viewSvc.ChangePrimaryView
        return activateViewFunc

    def _HandleSessionChangeInStation(self, isRemote, session, change, viewSvc):
        if 'stationid' in change:
            self.LogNotice('GameUI::OnSessionChanged, Heading for station', isRemote, session, change)
            activateViewFunc = self._GetActivateViewFunction(viewSvc)
            view = self._GetStationView()
            uthread.pool('GameUI::ActivateView::station', activateViewFunc, view, change=change)

    def _HandleSessionChangeInWorldSpace(self, isRemote, session, change, viewSvc):
        if 'worldspaceid' in change:
            self.LogWarn('GameUI::OnSessionChanged, Heading for worldspace', isRemote, session, change)
            activateViewFunc = self._GetActivateViewFunction(viewSvc)
            uthread.pool('GameUI::ActivateView::worldspace', activateViewFunc, 'worldspace', change=change)

    def _HandleSessionChangeInStructure(self, isRemote, session, change, viewSvc):
        structureView = self._GetStructureView()
        if 'structureid' in change:
            wasPodded, _, changedToStructureFromSpace = self._WasCharacterPodded(change)
            self.LogNotice('GameUI::OnSessionChanged, Heading for structure', isRemote, session, change)
            if wasPodded:
                structureView = ViewState.Hangar
                settings.user.ui.Set('defaultStructureView', structureView)
            uthread.pool('GameUI::ActivateView::structure', self._GetActivateViewFunction(viewSvc), structureView, change=change)
            ballpark = sm.GetService('michelle').GetBallpark()
            if ballpark and ballpark.solarsystemID == session.solarsystemid2:
                if session.structureid in ballpark.balls:
                    ballpark.ego = session.structureid
                    self.OnNewState(ballpark)
                else:
                    self.wannaBeEgo = session.structureid
        elif 'shipid' in change:
            if session.shipid == session.structureid:
                if not self.viewState.IsViewActive('inflight'):
                    uthread.pool('GameUI::ActivateView::structure', self._GetActivateViewFunction(viewSvc), 'inflight', change=change)
            elif not self.viewState.IsViewActive('structure', 'hangar'):
                uthread.pool('GameUI::ActivateView::structure', self._GetActivateViewFunction(viewSvc), structureView, change=change)

    def _HandleSessionChangeInSpace(self, isRemote, session, change, viewSvc):
        if 'solarsystemid' in change:
            oldSolarSystemID, newSolarSystemID = change['solarsystemid']
            if oldSolarSystemID:
                sm.GetService('FxSequencer').ClearAll()
                self.LogInfo('Cleared effects')
            self.LogNotice('GameUI::OnSessionChanged, Heading for inflight', isRemote, session, change)
            activateViewFunc = self._GetActivateViewFunction(viewSvc)
            uthread.pool('GameUI::ChangePrimaryView::inflight', activateViewFunc, 'inflight', change=change)
        else:
            if 'shipid' in change and change['shipid'][1] is not None:
                michelle = sm.GetService('michelle')
                bp = michelle.GetBallpark()
                if bp:
                    if change['shipid'][0]:
                        self.KillCargoView(change['shipid'][0])
                    uthread.new(sm.GetService('target').ClearTargets)
                    if session.shipid in bp.balls:
                        self.LogNotice('Changing ego:', bp.ego, '->', session.shipid)
                        bp.ego = session.shipid
                        self.OnNewState(bp)
                    else:
                        self.LogNotice('Postponing ego:', bp.ego, '->', session.shipid)
                        self.wannaBeEgo = session.shipid
            if 'structureid' in change:
                self.LogNotice('GameUI::OnSessionChanged, Heading for inflight', isRemote, session, change)
                uthread.pool('GameUI::ChangePrimaryView::inflight', self._GetActivateViewFunction(viewSvc), 'inflight', change=change)
                ballpark = sm.GetService('michelle').GetBallpark()
                if ballpark:
                    if session.shipid in ballpark.balls:
                        ballpark.ego = session.shipid
                        self.OnNewState(ballpark)
                    else:
                        self.wannaBeEgo = session.shipid
            if 'shipid' in change and 'structureid' in change:
                uicore.layer.shipui.CloseView()

    def KillCargoView(self, id_, guidsToKill = None):
        if guidsToKill is None:
            guidsToKill = ('form.ShipCargo', 'form.LootCargoView', 'form.DroneBay', 'form.CorpHangar', 'form.CorpHangarArray', 'form.SpecialCargoBay', 'form.PlanetInventory')
        for each in uicore.registry.GetWindows()[:]:
            if getattr(each, '__guid__', None) in guidsToKill and getattr(each, 'itemID', None) == id_:
                if not each.destroyed:
                    if hasattr(each, 'Close'):
                        each.Close()
                    else:
                        each.CloseByUser()

    def ScopeCheck(self, scope = None):
        if scope is None:
            scope = []
        scope += ['all']
        self.currentScope = scope
        for each in uicore.registry.GetWindows()[:]:
            if getattr(each, 'content', None) and hasattr(each.content, 'scope') and each.content.scope:
                if each.content.scope not in scope:
                    if each is not None and not each.destroyed:
                        if hasattr(each, 'Close'):
                            self.LogInfo('ScopeCheck::Close', each.name, 'scope', scope)
                            each.Close()
                        else:
                            self.LogInfo('ScopeCheck::Close', each.name, 'scope', scope)
                            each.CloseByUser()
            elif getattr(each, 'scope', None) and each.scope not in scope:
                if each is not None and not each.destroyed:
                    if hasattr(each, 'Close'):
                        self.LogInfo('ScopeCheck::Close2', each.name, 'scope', scope)
                        each.Close()
                    else:
                        self.LogInfo('ScopeCheck::Close2', each.name, 'scope', scope)
                        each.CloseByUser()

    def GetCurrentScope(self):
        return self.currentScope

    def FirewallCheck(self):
        if boot.region == 'optic':
            url = 'http://www.eve-online.com.cn'
        else:
            url = 'http://www.eveonline.com'
        url = url + '/firewallcheck.htm'
        try:
            urllib2.urlopen(url)
        except:
            sys.exc_clear()

    def StartupUI(self, *args):
        uthread.new(_ScheduleBackgroundDownloads)
        self.usingSingleSignOn = False
        uicore.SetFontHandler(EveFontHandler())
        uicore.SetAudioHandler(sm.StartService('audio'))
        uicore.Startup(self.uiLayerList)
        desktopIndex = uicore.desktop.children.index(uicore.layer.hint)
        self.resourceLoadingIndicator = ResourceLoadingIndicator(parent=uicore.desktop, align=uiconst.BOTTOMLEFT, pos=(12, 12, 32, 32), isGlobal=True, idx=desktopIndex)
        uicore.SetCommandHandler(sm.StartService('cmd'))
        import eve.client.script.ui.control.tooltips as tooltipHandler
        uicore.SetTooltipHandler(tooltipHandler)
        uicore.Message = eve.Message
        uiutil.AskName = uiutil.NamePopup
        log.SetUiMessageFunc(uicore.Message)
        if blue.sysinfo.isTransgaming:
            sm.StartService('cider')
        SetupViewStates(self.viewState, uicore.layer.viewstate)
        sm.GetService('device').SetupUIScaling()
        sceneManager = sm.StartService('sceneManager')
        sceneManager.SetSceneType(SCENE_TYPE_SPACE)
        sceneManager.Initialize(trinity.EveSpaceScene())
        self.RegisterBlueResources()
        sm.StartService('connection')
        sm.StartService('logger')
        sm.StartService('vivox')
        sm.StartService('ownerprimer')
        sm.StartService('petition')
        sm.StartService('ui')
        sm.StartService('window')
        sm.StartService('log')
        sm.StartService('consider')
        sm.StartService('incursion')
        sm.StartService('cameraClient')
        sm.StartService('moonScan')
        sm.StartService('preview')
        sm.StartService('crimewatchSvc')
        sm.StartService('flightPredictionSvc')
        sm.StartService('flightControls')
        sm.StartService('sensorSuite')
        sm.StartService('hackingUI')
        sm.StartService('radialmenu')
        sm.StartService('tourneyUISvc')
        sm.StartService('achievementSvc')
        sm.StartService('tacticalNavigation')
        uicore.megaMenuManager = MegaMenuManager()
        if blue.win32:
            try:
                blue.win32.WTSRegisterSessionNotification(trinity.device.GetWindow(), 0)
                uicore.uilib.SessionChangeHandler = self.OnWindowsUserSessionChange
            except:
                sys.exc_clear()
                uicore.uilib.SessionChangeHandler = None

        sm.GetService('launcher').SetClientBootProgress(60)
        token = None
        for arg in blue.pyos.GetArg()[1:]:
            if arg.startswith('/ssoToken'):
                try:
                    argName, token = arg.split('=')
                except:
                    raise RuntimeError('Invalid format of SSO token, should be /ssoToken=<token>')

        pr = sm.GetService('webtools').GetVars()
        if pr:
            sm.GetService('webtools').GoSlimLogin()
        elif token is not None:
            self.usingSingleSignOn = True
            self.DoLogin(token)
        else:
            self.viewState.ActivateView('login')

    def RegisterBlueResources(self):
        from carbon.client.script.graphics.resourceConstructors.caustics import Caustics
        blue.resMan.RegisterResourceConstructor('caustics', Caustics)
        from carbon.client.script.graphics.resourceConstructors.gradients import Gradient, GradientRadial, Gradient2D
        blue.resMan.RegisterResourceConstructor('gradient', Gradient)
        blue.resMan.RegisterResourceConstructor('gradient_radial', GradientRadial)
        blue.resMan.RegisterResourceConstructor('gradient2d', Gradient2D)
        from eve.client.script.ui.station.captainsquarters.screens import SetupCqMainScreen, SetupCqAgentFinderScreen, SetupCqPIScreen, SetupCqStationLogo
        blue.resMan.RegisterResourceConstructor('CqMainScreen', SetupCqMainScreen)
        blue.resMan.RegisterResourceConstructor('CqAgentFinderScreen', SetupCqAgentFinderScreen)
        blue.resMan.RegisterResourceConstructor('cqpiscreen', SetupCqPIScreen)
        blue.resMan.RegisterResourceConstructor('stationlogo', SetupCqStationLogo)

    def EnableResourceLoadingIndicator(self):
        if not self.resourceLoadingIndicator.destroyed:
            self.resourceLoadingIndicator.Enable()

    def DisableResourceLoadingIndicator(self):
        if not self.resourceLoadingIndicator.destroyed:
            self.resourceLoadingIndicator.Disable()

    def DoLogin(self, token):
        sm.ScatterEvent('OnClientReady', 'login')
        try:
            sm.GetService('launcher').SetClientBootProgress(70)
            sm.GetService('connection').LoginSso(token)
        except:
            sm.GetService('loading').CleanUp()
            self.viewState.ActivateView('login')
            raise

    def SetLanguage(self, key):
        if boot.region == 'optic' and not eve.session.role & service.ROLEMASK_ELEVATEDPLAYER:
            key = 'ZH'
        convertedKey = localization.util.ConvertLanguageIDFromMLS(key)
        if convertedKey in localization.GetLanguages() and key != prefs.languageID:
            if session.userid is not None:
                sm.RemoteSvc('authentication').SetLanguageID(key)
            else:
                session.__dict__['languageID'] = key
            prefs.languageID = key
            localization.LoadLanguageData()
            sm.ChainEvent('ProcessUIRefresh')
            sm.ScatterEvent('OnUIRefresh')

    def HasActiveOverlay(self):
        return sm.IsServiceRunning('viewState') and self.viewState.IsCurrentViewSecondary()

    def GoLogin(self, step = 1, connectionLost = 0, *args):
        blue.statistics.SetTimelineSectionName('login')

    def GoCharacterCreationCurrentCharacter(self, *args):
        if None in (session.charid, session.genderID, session.bloodlineID):
            return
        if self.viewState.IsViewActive('charactercreation'):
            return
        stationSvc = sm.GetService('station')
        dollState = stationSvc.GetPaperdollStateCache()
        msg = None
        if dollState == const.paperdollStateResculpting:
            msg = 'AskRecustomizeCharacter'
        elif dollState == const.paperdollStateFullRecustomizing:
            msg = 'AskRecustomizeCharacterChangeBloodline'
        message = uiconst.ID_NO
        if msg is not None:
            message = eve.Message(msg, {'charName': cfg.eveowners.Get(session.charid).ownerName}, uiconst.YESNO, default=uiconst.ID_NO, suppress=uiconst.ID_NO)
        if message == uiconst.ID_YES:
            self.GoCharacterCreation(session.charid, session.genderID, session.bloodlineID, dollState=dollState)
            stationSvc.ClearPaperdollStateCache()
        elif message == uiconst.ID_NO:
            self.GoCharacterCreation(session.charid, session.genderID, session.bloodlineID, dollState=const.paperdollStateNoRecustomization)

    def GoCharacterCreation(self, charID = None, gender = None, bloodlineID = None, askUseLowShader = True, dollState = None, *args):
        if sm.GetService('station').exitingstation:
            return
        everesourceprefetch.PullToFront('ui_cc')
        if askUseLowShader:
            msg = uiconst.ID_YES
            if not sm.StartService('device').SupportsSM3():
                msg = eve.Message('AskMissingSM3', {}, uiconst.YESNO, default=uiconst.ID_NO)
            if msg != uiconst.ID_YES:
                return
            msg = uiconst.ID_YES
            if ccUtil.SupportsHigherShaderModel():
                msg = eve.Message('AskUseLowShader', {}, uiconst.YESNO, default=uiconst.ID_NO)
            if msg != uiconst.ID_YES:
                return
        self.viewState.ActivateView('charactercreation', charID=charID, gender=gender, bloodlineID=bloodlineID, dollState=dollState)

    def HasDisconnectionNotice(self):
        return form.MessageBox.IsOpen(windowID='DisconnectNotice')

    def MessageBox(self, text, title = 'EVE', buttons = None, icon = None, suppText = None, customicon = None, height = None, blockconfirmonreturn = 0, default = None, modal = True, msgkey = None, messageData = None):
        if not getattr(uicore, 'desktop', None):
            return
        if self.HasDisconnectionNotice():
            return (default, False)
        if buttons is None:
            buttons = uiconst.ID_OK
        msgbox = form.MessageBox.Open(useDefaultPos=True)
        msgbox.state = uiconst.UI_HIDDEN
        msgbox.isModal = modal
        msgbox.blockconfirmonreturn = blockconfirmonreturn
        if msgkey is not None and msgkey in CUSTOM_MESSAGE_BOXES:
            msgbox.ExecuteCustomContent(CUSTOM_MESSAGE_BOXES[msgkey], title, buttons, icon, suppText, customicon, height, default=default, modal=modal, messageData=messageData)
        else:
            msgbox.Execute(text, title, buttons, icon, suppText, customicon, height, default=default, modal=modal)
        if modal:
            ret = msgbox.ShowModal()
        else:
            ret = msgbox.ShowDialog()
        return (ret, msgbox.suppress)

    def RadioButtonMessageBox(self, text, title = 'EVE', buttons = None, icon = None, suppText = None, customicon = None, radioOptions = None, height = None, width = None, blockconfirmonreturn = 0, default = None, modal = True):
        if radioOptions is None:
            radioOptions = []
        if not getattr(uicore, 'desktop', None):
            return
        if self.HasDisconnectionNotice():
            return (default, False)
        if buttons is None:
            buttons = uiconst.ID_OK
        msgbox = form.RadioButtonMessageBox.Open(useDefaultPos=True)
        msgbox.isModal = modal
        msgbox.blockconfirmonreturn = blockconfirmonreturn
        msgbox.Execute(text, title, buttons, radioOptions, icon, suppText, customicon, height, width=width, default=default, modal=modal)
        if modal:
            buttonResult = msgbox.ShowModal()
            radioSelection = msgbox.GetRadioSelection()
            ret = (buttonResult, radioSelection)
        else:
            buttonResult = msgbox.ShowDialog()
            radioSelection = msgbox.GetRadioSelection()
            ret = (buttonResult, radioSelection)
        return (ret, msgbox.suppress)

    def Say(self, msgtext, time = 100):
        for each in uicore.layer.abovemain.children[:]:
            if each.name == 'message':
                each.ShowMsg(msgtext)
                return

        message = uicls.Message(parent=uicore.layer.abovemain, name='message')
        message.ShowMsg(msgtext)

    def DoBallsAdded(self, *args, **kw):
        import stackless
        import blue
        t = stackless.getcurrent()
        timer = t.PushTimer(blue.pyos.taskletTimer.GetCurrent() + '::gameui')
        try:
            return self.DoBallsAdded_(*args, **kw)
        finally:
            t.PopTimer(timer)

    def DoBallsAdded_(self, lst):
        for each in lst:
            self.DoBallAdd(*each)

    def DoBallAdd(self, ball, slimItem):
        if ball.id == self.wannaBeEgo:
            bp = sm.GetService('michelle').GetBallpark()
            self.LogNotice('Post-ego change: ', bp.ego, '->', self.wannaBeEgo)
            bp.ego = self.wannaBeEgo
            self.wannaBeEgo = -1
            self.OnNewState(bp)

    def DoBallClear(self, solItem):
        uthread.new(self._DoBallClear, solItem)

    def _DoBallClear(self, solItem):
        sm.GetService('tactical').TearDownOverlay()
        sc = self.sceneManager.GetScene()
        spaceToSpaceTransition = self.viewState.GetTransitionByName('inflight', 'inflight')
        if spaceToSpaceTransition.active:
            spaceToSpaceTransition.Finalize()
        else:
            self.sceneManager.UnregisterScene('default', ignoreCamera=True)
            self.sceneManager.LoadScene(sc, registerKey='default')
            self.sceneManager.ApplySpaceScene()
        if eve.session.solarsystemid:
            sm.GetService('tactical').CheckInit()

    def OnNewState(self, bp):
        uthread.pool('GameUI::New shipui state', self._NewState, bp)

    @telemetry.ZONE_METHOD
    def _NewState(self, bp):
        if bp and bp.balls.get(bp.ego, None):
            if util.InSpace():
                if not uicore.layer.shipui.isopen:
                    uicore.layer.shipui.OpenView()
                else:
                    uicore.layer.shipui.SetupShip(False)
            camera = sm.GetService('sceneManager').GetActiveSpaceCamera()
            camera.LookAtMaintainDistance(bp.ego)

    def DoWindowIdentification(self):
        if eve.session.charid:
            charName = cfg.eveowners.Get(eve.session.charid).name
            trinity.app.title = '%s - %s' % (uicore.triappargs['title'], charName)
        else:
            trinity.app.title = uicore.triappargs['title']

    def TryOpenLanguageWindow(self):
        if boot.region == 'optic' or session.languageID == 'EN':
            return
        if settings.user.suppress.Get('suppress.Bilingual_suppressMessage', False):
            return
        blue.synchro.SleepWallclock(5000)
        LanguageWindow.Open()

    def OnWindowsUserSessionChange(self, wp, lp):
        audio = sm.GetService('audio')
        if wp == 1:
            sm.GetService('vivox').OnSessionReconnect()
            if audio.IsActivated() and audio.GetMasterVolume() > 0.0:
                audio.SetMasterVolume(audio.GetMasterVolume(), persist=True)
        elif wp == 2:
            sm.GetService('vivox').OnSessionDisconnect()
            if audio.IsActivated() and audio.GetMasterVolume() > 0.0:
                audio.SetMasterVolume(0.0, persist=False)

    def ProcessActiveShipChanged(self, shipID, oldShipID):
        if oldShipID:
            self.KillCargoView(oldShipID)

    def UsingSingleSignOn(self):
        return getattr(self, 'usingSingleSignOn', False)

    def OnShowMarketDetails(self, typeID):
        sm.GetService('marketutils').ShowMarketDetails(typeID, None, True)

    def OnShowOwnerDetailsWindow(self, targetID):
        if util.IsCharacter(targetID):
            sm.GetService('info').ShowInfo(const.typeCharacterGallente, targetID)
        elif util.IsCorporation(targetID):
            sm.GetService('info').ShowInfo(const.typeCorporation, targetID)
        elif util.IsAlliance(targetID):
            sm.GetService('info').ShowInfo(const.typeAlliance, targetID)

    def OnCreateNewMailWindow(self, recipients, corpOrAllianceRecipient, toListID, subject, body):
        sm.GetService('mailSvc').SendMsgDlg(toCharacterIDs=recipients, toCorpOrAllianceID=corpOrAllianceRecipient, toListID=toListID, subject=subject, body=body)

    def OnShowContract(self, contractID):
        sm.GetService('contracts').ShowContract(contractID)


def _ScheduleBackgroundDownloads():
    everesourceprefetch.PrepareFilesets()
    keys = ['staticdata',
     'ui_basics',
     'ui_classes',
     'black_files',
     'low_detail_ships',
     'medium_detail_ships',
     'ui_cc']
    for each in keys:
        everesourceprefetch.Schedule(each)
