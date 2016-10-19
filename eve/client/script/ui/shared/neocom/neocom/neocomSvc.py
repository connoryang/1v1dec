#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\neocom\neocomSvc.py
import collections
import blue
import carbonui.const as uiconst
import localization
import neocomPanelEntries
import service
import uicontrols
import uiutil
import uthread
import util
from achievements.client.achievementTreeWindow import AchievementTreeWindow
from eve.client.script.ui.control.browser.eveBrowserWindow import BrowserWindow
from eve.client.script.ui.control.eveWindowStack import WindowStack
from eve.client.script.ui.services.redeemsvc import RedeemWindow
from eve.client.script.ui.services.tutorialWindow import TutorialWindow
from eve.client.script.ui.shared.addressBookWindow import AddressBookWindow
from eve.client.script.ui.shared.agentFinder import AgentFinderWnd
from eve.client.script.ui.shared.assetsWindow import AssetsWindow
from eve.client.script.ui.shared.bountyWindow import BountyWindow
from eve.client.script.ui.shared.comtool.lscchannel import Channel
from eve.client.script.ui.shared.eveCalendar import CalendarWnd
from eve.client.script.ui.shared.fitting.fittingWnd import FittingWindow2
from eve.client.script.ui.shared.fittingMgmtWindow import FittingMgmt
from eve.client.script.ui.shared.fleet.fleetwindow import FleetWindow
from eve.client.script.ui.shared.industry.industryWnd import Industry
from eve.client.script.ui.shared.inventory.invWindow import InventoryPrimary, ActiveShipCargo, StationItems, StationShips, StationCorpHangars, StationCorpDeliveries
from eve.client.script.ui.shared.mapView.mapViewPanel import MapViewPanel
from eve.client.script.ui.shared.mapView.mapViewUtil import IsMapBetaEnabled
from eve.client.script.ui.shared.maps.browserwindow import MapBrowserWnd
from eve.client.script.ui.shared.market.marketbase import RegionalMarket
from eve.client.script.ui.shared.neocom.calculator import Calculator
from eve.client.script.ui.shared.neocom.channels import Channels
from eve.client.script.ui.shared.neocom.characterSheetWindow import CharacterSheetWindow
from eve.client.script.ui.shared.neocom.compare import TypeCompare
from eve.client.script.ui.shared.neocom.contracts.contractsWnd import ContractsWindow
from eve.client.script.ui.shared.neocom.corporation.base_corporation_ui import CorporationWindow
from eve.client.script.ui.shared.neocom.evemail import MailWindow
from eve.client.script.ui.shared.neocom.help import HelpWindow
from eve.client.script.ui.shared.neocom.journal import JournalWindow
from eve.client.script.ui.shared.neocom.neocom.neocomCommon import BTNTYPE_WINDOW
from eve.client.script.ui.shared.neocom.notepad import NotepadWindow
from eve.client.script.ui.shared.neocom.wallet import WalletWindow
from eve.client.script.ui.shared.planet.planetWindow import PlanetWindow
from eve.client.script.ui.shared.twitch.twitchStreaming import TwitchStreaming
from eve.client.script.ui.shared.uilog import LoggerWindow
from eve.client.script.ui.station.fw.base_fw import MilitiaWindow
from eve.client.script.ui.station.securityOfficeWindow import SecurityOfficeWindow
from eve.client.script.ui.structure.accessGroups.accesGroupsWnd import AccessGroupsWnd
from eve.client.script.ui.structure.structureBrowser.structureBrowserWnd import StructureBrowserWnd
from projectdiscovery.client.projectdiscoveryClientSvc import PROJECT_DISCOVERY_ID
from projectdiscovery.client.window import ProjectDiscoveryWindow
from seasons.client.const import SCOPE_LOGO_RES_PATH, get_seasons_title_label_path
from seasons.client.seasonwindow import SeasonWindow
from seasons.common.const import SEASONAL_EVENTS_ID
from . import neocomCommon
from .neocom import Neocom
from .neocomPanels import PanelEveMenu, PanelBase
DEBUG_ALWAYSLOADRAW = False
NOTPERSISTED_BTNTYPES = (neocomCommon.BTNTYPE_WINDOW,)
RAWDATA_NEOCOMDEFAULT = [(neocomCommon.BTNTYPE_CHAT, 'chat', None),
 (neocomCommon.BTNTYPE_CMD, 'inventory', None),
 (neocomCommon.BTNTYPE_CMD, 'addressbook', None),
 (neocomCommon.BTNTYPE_CMD, 'mail', None),
 (neocomCommon.BTNTYPE_CMD, 'fitting', None),
 (neocomCommon.BTNTYPE_CMD, 'market', None),
 (neocomCommon.BTNTYPE_CMD, 'industry', None),
 (neocomCommon.BTNTYPE_CMD, 'corporation', None),
 (neocomCommon.BTNTYPE_CMD, 'fleet', None),
 (neocomCommon.BTNTYPE_CMD, 'map', None),
 (neocomCommon.BTNTYPE_CMD, 'map_beta', None),
 (neocomCommon.BTNTYPE_CMD, 'shipTree', None),
 (neocomCommon.BTNTYPE_CMD, 'assets', None),
 (neocomCommon.BTNTYPE_CMD, 'wallet', None),
 (neocomCommon.BTNTYPE_CMD, 'journal', None),
 (neocomCommon.BTNTYPE_CMD, 'aurumStore', None),
 (neocomCommon.BTNTYPE_CMD, 'opportunities', None),
 (neocomCommon.BTNTYPE_CMD, 'tutorial', None),
 (neocomCommon.BTNTYPE_CMD, 'help', None)]
RAWDATA_EVEMENU = [(neocomCommon.BTNTYPE_GROUP, 'groupInventory', [(neocomCommon.BTNTYPE_CMD, 'inventory', None),
   (neocomCommon.BTNTYPE_CMD, 'activeShipCargo', None),
   (neocomCommon.BTNTYPE_CMD, 'itemHangar', None),
   (neocomCommon.BTNTYPE_CMD, 'shipHangar', None),
   (neocomCommon.BTNTYPE_CMD, 'corpHangar', None),
   (neocomCommon.BTNTYPE_CMD, 'corpDeliveriesHangar', None),
   (neocomCommon.BTNTYPE_CMD, 'assets', None),
   (neocomCommon.BTNTYPE_CMD, 'redeemItems', None)]),
 (neocomCommon.BTNTYPE_GROUP, 'groupAccessories', [(neocomCommon.BTNTYPE_BOOKMARKS, 'bookmarkedsites', None),
   (neocomCommon.BTNTYPE_CMD, 'browser', None),
   (neocomCommon.BTNTYPE_CMD, 'calculator', None),
   (neocomCommon.BTNTYPE_CMD, 'notepad', None),
   (neocomCommon.BTNTYPE_CMD, 'log', None)]),
 (neocomCommon.BTNTYPE_GROUP, 'groupBusiness', [(neocomCommon.BTNTYPE_CMD, 'market', None),
   (neocomCommon.BTNTYPE_CMD, 'contracts', None),
   (neocomCommon.BTNTYPE_CMD, 'wallet', None),
   (neocomCommon.BTNTYPE_CMD, 'industry', None),
   (neocomCommon.BTNTYPE_CMD, 'planets', None),
   (neocomCommon.BTNTYPE_CMD, 'agentfinder', None),
   (neocomCommon.BTNTYPE_CMD, 'militia', None),
   (neocomCommon.BTNTYPE_CMD, 'bountyoffice', None),
   (neocomCommon.BTNTYPE_CMD, 'structurebrowser', None),
   (neocomCommon.BTNTYPE_CMD, 'accessgroups', None)]),
 (neocomCommon.BTNTYPE_GROUP, 'groupSocial', [(neocomCommon.BTNTYPE_CMD, 'mail', None),
   (neocomCommon.BTNTYPE_CMD, 'calendar', None),
   (neocomCommon.BTNTYPE_CMD, 'corporation', None),
   (neocomCommon.BTNTYPE_CMD, 'sovdashboard', None),
   (neocomCommon.BTNTYPE_CMD, 'fleet', None),
   (neocomCommon.BTNTYPE_TWITCH, 'twitch', None),
   (neocomCommon.BTNTYPE_CMD, 'chatchannels', None)]),
 (neocomCommon.BTNTYPE_CMD, 'charactersheet', None),
 (neocomCommon.BTNTYPE_CMD, 'addressbook', None),
 (neocomCommon.BTNTYPE_CMD, 'fitting', None),
 (neocomCommon.BTNTYPE_CMD, 'fittingMgmt', None),
 (neocomCommon.BTNTYPE_CMD, 'map_old', None),
 (neocomCommon.BTNTYPE_CMD, 'map_beta', None),
 (neocomCommon.BTNTYPE_CMD, 'shipTree', None),
 (neocomCommon.BTNTYPE_CMD, 'journal', None),
 (neocomCommon.BTNTYPE_CMD, 'compareTool', None),
 (neocomCommon.BTNTYPE_CMD, 'aurumStore', None),
 (neocomCommon.BTNTYPE_CMD, 'tutorial', None),
 (neocomCommon.BTNTYPE_CMD, 'opportunities', None)]
RAWDATA_EVEMENU_DEFAULT = [(neocomCommon.BTNTYPE_CMD, 'help', None), (neocomCommon.BTNTYPE_CMD, 'settings', None)]
SCOPE_NETWORK_BTN = (neocomCommon.BTNTYPE_CMD, SEASONAL_EVENTS_ID, None)

class BtnDataRaw():

    def __init__(self, label = None, cmdName = None, iconPath = None, wndCls = None):
        self.label = label
        self.cmdName = cmdName
        self.iconPath = iconPath
        self.wndCls = wndCls


BTNDATARAW_BY_ID = {'addressbook': BtnDataRaw(cmdName='OpenPeopleAndPlaces', wndCls=AddressBookWindow),
 'agentfinder': BtnDataRaw(cmdName='OpenAgentFinder', wndCls=AgentFinderWnd),
 'assets': BtnDataRaw(cmdName='OpenAssets', wndCls=AssetsWindow),
 'bookmarkedsites': BtnDataRaw(label='UI/Neocom/BrowserBookmarksBtn', iconPath='res:/UI/Texture/windowIcons/browserbookmarks.png'),
 'bountyoffice': BtnDataRaw(cmdName='OpenBountyOffice', wndCls=BountyWindow),
 'browser': BtnDataRaw(cmdName='OpenBrowser', wndCls=BrowserWindow),
 'calculator': BtnDataRaw(cmdName='OpenCalculator', wndCls=Calculator),
 'calendar': BtnDataRaw(cmdName='OpenCalendar', wndCls=CalendarWnd),
 'charactersheet': BtnDataRaw(cmdName='OpenCharactersheet', wndCls=CharacterSheetWindow),
 'chat': BtnDataRaw(wndCls=Channel, label='UI/Chat/ChannelWindow/Channels'),
 'chatchannels': BtnDataRaw(cmdName='OpenChannels', wndCls=Channels),
 'contracts': BtnDataRaw(cmdName='OpenContracts', wndCls=ContractsWindow),
 'corporation': BtnDataRaw(cmdName='OpenCorporationPanel', wndCls=CorporationWindow),
 'fitting': BtnDataRaw(cmdName='OpenFitting', wndCls=FittingWindow2),
 'fittingMgmt': BtnDataRaw(cmdName='OpenFittingMgmt', wndCls=FittingMgmt),
 'fleet': BtnDataRaw(cmdName='OpenFleet', wndCls=FleetWindow),
 'group': BtnDataRaw(label='UI/Neocom/ButtonGroup', iconPath=neocomCommon.ICONPATH_GROUP),
 'groupInventory': BtnDataRaw(label='UI/Neocom/GroupInventory', iconPath=neocomCommon.ICONPATH_GROUP),
 'groupAccessories': BtnDataRaw(label='UI/Neocom/GroupAccessories', iconPath=neocomCommon.ICONPATH_GROUP),
 'groupBusiness': BtnDataRaw(label='UI/Neocom/GroupBusiness', iconPath=neocomCommon.ICONPATH_GROUP),
 'groupSocial': BtnDataRaw(label='UI/Neocom/GroupSocial', iconPath=neocomCommon.ICONPATH_GROUP),
 'help': BtnDataRaw(cmdName='OpenHelp', wndCls=HelpWindow),
 'inventory': BtnDataRaw(cmdName='OpenInventory', wndCls=InventoryPrimary),
 'activeShipCargo': BtnDataRaw(cmdName='OpenCargoHoldOfActiveShip', wndCls=ActiveShipCargo),
 'itemHangar': BtnDataRaw(cmdName='OpenHangarFloor', wndCls=StationItems),
 'shipHangar': BtnDataRaw(cmdName='OpenShipHangar', wndCls=StationShips),
 'corpHangar': BtnDataRaw(cmdName='OpenCorpHangar', wndCls=StationCorpHangars),
 'corpDeliveriesHangar': BtnDataRaw(cmdName='OpenCorpDeliveries', wndCls=StationCorpDeliveries),
 'journal': BtnDataRaw(cmdName='OpenJournal', wndCls=JournalWindow),
 'log': BtnDataRaw(cmdName='OpenLog', wndCls=LoggerWindow),
 'mail': BtnDataRaw(cmdName='OpenMail', wndCls=MailWindow),
 'map': BtnDataRaw(cmdName='CmdToggleMap', iconPath='res:/UI/Texture/windowIcons/map.png'),
 'map_old': BtnDataRaw(cmdName='CmdToggleMap', iconPath='res:/UI/Texture/windowIcons/map.png'),
 'map_beta': BtnDataRaw(cmdName='CmdToggleMapBeta', iconPath='res:/UI/Texture/windowIcons/map.png'),
 'shipTree': BtnDataRaw(cmdName='CmdToggleShipTree', iconPath='res:/ui/texture/windowIcons/ISIS.png'),
 'market': BtnDataRaw(cmdName='OpenMarket', wndCls=RegionalMarket),
 'militia': BtnDataRaw(cmdName='OpenMilitia', wndCls=MilitiaWindow),
 'navyoffices': BtnDataRaw(wndCls=MilitiaWindow),
 'notepad': BtnDataRaw(cmdName='OpenNotepad', wndCls=NotepadWindow),
 'industry': BtnDataRaw(label='UI/Neocom/IndustryBtn', cmdName='OpenIndustry', wndCls=Industry),
 'planets': BtnDataRaw(label='UI/ScienceAndIndustry/PlanetaryColonies', cmdName='OpenPlanets', wndCls=PlanetWindow),
 'tutorial': BtnDataRaw(cmdName='OpenTutorial', wndCls=TutorialWindow),
 'wallet': BtnDataRaw(cmdName='OpenWallet', wndCls=WalletWindow),
 'settings': BtnDataRaw(cmdName='CmdToggleSystemMenu', iconPath='res:/ui/texture/WindowIcons/settings.png'),
 'securityoffice': BtnDataRaw(cmdName='OpenSecurityOffice', wndCls=SecurityOfficeWindow),
 'compareTool': BtnDataRaw(cmdName='OpenCompare', wndCls=TypeCompare),
 'twitch': BtnDataRaw(cmdName='OpenTwitchStreaming', wndCls=TwitchStreaming),
 'aurumStore': BtnDataRaw(cmdName='ToggleAurumStore', iconPath='res:/ui/texture/WindowIcons/NES.png'),
 'redeemItems': BtnDataRaw(cmdName='ToggleRedeemItems', wndCls=RedeemWindow),
 'opportunities': BtnDataRaw(cmdName='ToggleOpportunity', wndCls=AchievementTreeWindow),
 'structurebrowser': BtnDataRaw(cmdName='OpenStructureBrowser', wndCls=StructureBrowserWnd),
 'accessgroups': BtnDataRaw(cmdName='OpenAccessGroupsWindow', wndCls=AccessGroupsWnd)}

def AddDefaultEveMenu():
    for button in RAWDATA_EVEMENU_DEFAULT:
        if button not in RAWDATA_EVEMENU:
            RAWDATA_EVEMENU.append(button)


def AddProjectDiscoveryIfEnabled():
    if sm.RemoteSvc('ProjectDiscovery').is_enabled():
        if PROJECT_DISCOVERY_ID not in BTNDATARAW_BY_ID:
            RAWDATA_NEOCOMDEFAULT.append((neocomCommon.BTNTYPE_CMD, PROJECT_DISCOVERY_ID, None))
            RAWDATA_EVEMENU[2][2].append((neocomCommon.BTNTYPE_CMD, PROJECT_DISCOVERY_ID, None))
            BTNDATARAW_BY_ID[PROJECT_DISCOVERY_ID] = BtnDataRaw(label=PROJECT_DISCOVERY_ID, cmdName='ToggleProjectDiscovery', iconPath='res:/ui/texture/WindowIcons/projectdiscovery.png', wndCls=ProjectDiscoveryWindow)


def AddScopeNetworkIfEnabled():
    if not sm.GetService('seasonService').is_season_active():
        if SEASONAL_EVENTS_ID in BTNDATARAW_BY_ID:
            RAWDATA_NEOCOMDEFAULT.remove(SCOPE_NETWORK_BTN)
            RAWDATA_EVEMENU.remove(SCOPE_NETWORK_BTN)
            del BTNDATARAW_BY_ID[SEASONAL_EVENTS_ID]
        return
    if SEASONAL_EVENTS_ID not in BTNDATARAW_BY_ID:
        BTNDATARAW_BY_ID[SEASONAL_EVENTS_ID] = BtnDataRaw(label=get_seasons_title_label_path(), cmdName='ToggleSeasonWindow', iconPath=SCOPE_LOGO_RES_PATH, wndCls=SeasonWindow)
        RAWDATA_NEOCOMDEFAULT.append(SCOPE_NETWORK_BTN)
        RAWDATA_EVEMENU.append(SCOPE_NETWORK_BTN)
    sm.GetService('cmd').AddSeasonWindowCommand()


def ConvertOldTypeOfRawData(rawData):
    if isinstance(rawData, tuple):
        if len(rawData) == 3:
            btnType, id, children = rawData
        else:
            btnType, id, iconPath, children = rawData
        return util.KeyVal(btnType=btnType, id=id, children=children)
    return rawData


class NeocomSvc(service.Service):
    __update_on_reload__ = 1
    __guid__ = 'svc.neocom'
    __notifyevents__ = ['OnSessionChanged',
     'OnWindowOpened',
     'OnWindowClosed',
     'OnWindowMinimized',
     'OnWindowMaximized']

    def Run(self, *args):
        self.eveMenu = None
        self.folderDropCookie = None
        self.currPanels = []
        self.neocom = None
        self.updatingWindowPush = False
        self.blinkQueue = []
        self.btnData = None
        self.blinkThread = None

    def Stop(self, memStream = None):
        self.CloseAllPanels()
        for cont in uicore.layer.sidePanels.children:
            if cont.name == 'Neocom':
                cont.Close()

        for cont in uicore.layer.abovemain.children:
            if isinstance(cont, PanelBase):
                cont.Close()

        if self.neocom:
            self.neocom.Close()
            self.neocom = None
        if self.blinkThread:
            self.blinkThread.kill()
            self.blinkThread = None

    def Reload(self):
        self.Stop()
        self.Run()
        if self.neocom:
            self.neocom.Close()
        self.CreateNeocom()
        self.UpdateNeocomButtons()

    def _CheckNewDefaultButtons(self, rawData):
        originalRawData = settings.char.ui.Get('neocomButtonRawDataOriginal', self._GetDefaultRawButtonData())
        newOriginalData = []
        for data in self._GetDefaultRawButtonData():
            data = ConvertOldTypeOfRawData(data)
            newOriginalData.append(data)
            if not self._IsWndIDInRawData(data.id, originalRawData):
                if not self._IsWndIDInRawData(data.id, rawData):
                    rawData.append(data)

        settings.char.ui.Set('neocomButtonRawDataOriginal', tuple(newOriginalData))

    def _GetDefaultRawButtonData(self):
        return RAWDATA_NEOCOMDEFAULT

    def _IsWndIDInRawData(self, checkWndID, rawData):
        if not rawData:
            return False
        for data in rawData:
            data = ConvertOldTypeOfRawData(data)
            if checkWndID == data.id or self._IsWndIDInRawData(checkWndID, data.children):
                return True

        return False

    def ResetEveMenuBtnData(self):
        self.eveMenuBtnData = BtnDataHeadNode('eveMenu', RAWDATA_EVEMENU, isRemovable=False, persistChildren=False)

    def OnSessionChanged(self, isRemote, sess, change):
        if 'stationid' in change or 'structureid' in change:
            self.scopeSpecificBtnData = self.GetScopeSpecificButtonData(recreate=True)
            self.UpdateNeocomButtons()

    def CreateNeocom(self):
        AddProjectDiscoveryIfEnabled()
        AddScopeNetworkIfEnabled()
        AddDefaultEveMenu()
        if not self.btnData:
            rawData = settings.char.ui.Get('neocomButtonRawData', self._GetDefaultRawButtonData())
            self._CheckNewDefaultButtons(rawData)
            if DEBUG_ALWAYSLOADRAW:
                rawData = self._GetDefaultRawButtonData()
            self.btnData = BtnDataHeadNode('neocom', rawData)
            self.scopeSpecificBtnData = None
            self.ResetEveMenuBtnData()
        if not self.neocom:
            self.neocom = Neocom(parent=uicore.layer.sidePanels, idx=0)
            for wnd in uicore.registry.GetWindows():
                self.OnWindowOpened(wnd)

            for blinkData in self.blinkQueue:
                self.Blink(*blinkData)

            self.blinkQueue = []
        if self.blinkThread:
            self.blinkThread.kill()
            self.blinkThread = None
        self.blinkThread = uthread.new(self._BlinkThread)

    def _BlinkThread(self):
        while True:
            blue.synchro.SleepWallclock(neocomCommon.BLINK_INTERVAL)
            sm.ChainEvent('ProcessNeocomBlinkPulse')

    def OnWindowOpened(self, wnd):
        if not self.neocom:
            return
        if not wnd or wnd.destroyed:
            return
        if not wnd.IsKillable() or self._IsWindowIgnored(wnd):
            return
        for btnHeadData in (self.btnData, self.scopeSpecificBtnData):
            if not btnHeadData:
                continue
            for btnData in btnHeadData.children:
                if btnData.btnType != neocomCommon.BTNTYPE_WINDOW and wnd.__class__ == btnData.wndCls:
                    BtnDataNode(parent=btnData, children=None, iconPath=btnData.iconPath, label=wnd.GetCaption(), id=wnd.windowID, btnType=neocomCommon.BTNTYPE_WINDOW, wnd=wnd, isDraggable=False)
                    btnData.SetActive()
                    return

        self.AddWindowButton(wnd)

    def ResetButtons(self):
        if uicore.Message('AskRestartNeocomButtons', {}, uiconst.YESNO) == uiconst.ID_YES:
            settings.char.ui.Set('neocomButtonRawData', None)
            settings.user.windows.Set('neocomWidth', Neocom.default_width)
            self.Reload()

    def _IsWindowIgnored(self, wnd):
        IGNORECLASSES = (WindowStack,
         Channel,
         MapBrowserWnd,
         MapViewPanel)
        for classType in IGNORECLASSES:
            if isinstance(wnd, classType):
                return True

        if wnd.isModal:
            return True
        return False

    def GetCmdNameForWindowFromRawData(self, wnd):
        for k, rButtonData in BTNDATARAW_BY_ID.iteritems():
            if rButtonData.wndCls == wnd.__class__:
                return getattr(rButtonData, 'cmdName', None)

    def AddWindowButton(self, wnd):
        btnData = self._GetBtnDataByGUID(wnd.__class__)
        if not btnData:
            btnData = BtnDataNode(parent=self.btnData, children=None, iconPath=wnd.iconNum, label=wnd.GetCaption(), id=wnd.__guid__, guid=wnd.__class__, btnType=BTNTYPE_WINDOW, isActive=True)
            cmdName = self.GetCmdNameForWindowFromRawData(wnd)
            btnData.cmdName = cmdName
        btnType = wnd.GetNeocomButtonType()
        cmdName = self.GetCmdNameForWindowFromRawData(wnd)
        childButtonData = BtnDataNode(parent=btnData, children=None, iconPath=wnd.iconNum, label=wnd.GetCaption(), id=wnd.windowID, btnType=btnType, wnd=wnd, isDraggable=False)
        if cmdName:
            childButtonData.cmdName = cmdName
        if btnData and btnData.btnUI:
            btnData.btnUI.UpdateIcon()

    def _GetBtnDataByGUID(self, guid):
        if not guid:
            return
        for btnHeadData in (self.btnData, self.scopeSpecificBtnData):
            if not btnHeadData:
                continue
            for btnData in btnHeadData.children:
                if getattr(btnData, 'guid', None) == guid:
                    return btnData

    def RemoveWindowButton(self, wndID, wndCaption, wndGUID):
        btnData = self._GetBtnDataByGUID(wndGUID)
        if not btnData:
            return
        for btnChildData in btnData.children:
            wnd = getattr(btnChildData, 'wnd', None)
            if not wnd or wnd.destroyed or wnd.windowID == wndID:
                btnChildData.Remove()
            elif not wnd.IsKillable() and not wnd.IsMinimized():
                btnChildData.Remove()

        if not btnData.children:
            if btnData.btnType == neocomCommon.BTNTYPE_WINDOW:
                btnData.Remove()
            else:
                btnData.SetInactive()

    def UpdateNeocomButtons(self):
        if self.neocom is not None:
            self.neocom.UpdateButtons()

    def OnWindowMinimized(self, wnd):
        if not self.neocom:
            return
        if not wnd or wnd.destroyed:
            return
        if not wnd.IsKillable():
            self.AddWindowButton(wnd)

    def OnWindowMaximized(self, wnd, wasMinimized):
        if not self.neocom:
            return
        if not wnd or wnd.destroyed:
            return
        if not wnd.IsKillable():
            self.RemoveWindowButton(wnd.windowID, wnd.GetCaption(), wnd.__class__)

    def OnWindowClosed(self, wndID, wndCaption, wndGUID):
        if not self.neocom:
            return
        self.RemoveWindowButton(wndID, wndCaption, wndGUID)

    def GetButtonData(self):
        return self.btnData.GetButtonsInScope()

    def GetScopeSpecificButtonData(self, recreate = False):
        if session.stationid is not None or session.structureid is not None:
            if recreate or self.scopeSpecificBtnData is None:
                self.scopeSpecificBtnData = self.GetStationButtonData()
        return self.scopeSpecificBtnData

    def GetStationButtonData(self):
        return None

    def GetMinimizeToPos(self, wnd):
        if not self.btnData:
            return (0, 0)
        else:
            if isinstance(wnd, uicontrols.WindowStack):
                wnd = wnd.GetActiveWindow()
            if isinstance(wnd, Channel):
                btnData = self.btnData.GetBtnDataByTypeAndID(neocomCommon.BTNTYPE_CHAT, 'chat')
            else:
                btnData = self._GetBtnDataByGUID(wnd.__class__)
            if btnData and btnData.btnUI:
                if btnData.btnUI.state == uiconst.UI_HIDDEN:
                    uiObj = self.neocom.overflowBtn
                else:
                    uiObj = btnData.btnUI
                uiObj.BlinkOnce()
                l, t, w, h = uiObj.GetAbsolute()
                return (l + w / 2, t + h / 2)
            uiObj = self.neocom.buttonCont.children[-1]
            if uiObj.state == uiconst.UI_HIDDEN:
                uiObj = self.neocom.overflowBtn
                uiObj.BlinkOnce()
            l, t, w, h = uiObj.GetAbsolute()
            return (l + w / 2, t + h / 2)

    def Blink(self, wndID, hint = None, numBlinks = None):
        if not self.neocom:
            self.blinkQueue.append((wndID, hint, numBlinks))
            return
        if not self.IsBlinkingEnabled():
            return
        if wndID == 'charactersheet':
            self.neocom.charSheetBtn.EnableBlink()
            return
        if wndID == 'calendar':
            if CalendarWnd.GetIfOpen():
                return
            btnData = self.btnData.GetBtnDataByTypeAndID(neocomCommon.BTNTYPE_CMD, wndID, recursive=True)
            if not btnData:
                self.neocom.clockCont.EnableBlink()
                return
        elif wndID == 'eveMenuBtn':
            self.eveMenuBtnData.isBlinking = True
            return
        headNodesToCheck = (self.btnData, self.scopeSpecificBtnData, self.eveMenuBtnData)
        for headBtnData in headNodesToCheck:
            if headBtnData is None:
                continue
            btnData = headBtnData.GetBtnDataByTypeAndID(neocomCommon.BTNTYPE_CMD, wndID, recursive=True)
            if btnData:
                btnData.SetBlinkingOn(hint, numBlinks)
                return

    def BlinkOff(self, wndID):
        if wndID == 'calendar':
            self.neocom.clockCont.DisableBlink()
        if not self.neocom:
            return
        btnData = self.btnData.GetBtnDataByTypeAndID(neocomCommon.BTNTYPE_CMD, wndID, recursive=True)
        if not btnData:
            return
        btnData.SetBlinkingOff()

    def OnNeocomButtonsRecreated(self):
        self.CloseAllPanels()

    def ShowPanel(self, triggerCont, panelClass, panelAlign, *args, **kw):
        panel = panelClass(idx=0, *args, **kw)
        self.currPanels.append(panel)
        uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEDOWN, self.OnGlobalMouseDown)
        self.CheckPanelPosition(panel, triggerCont, panelAlign)
        panel.EntryAnimation()
        return panel

    def CheckPanelPosition(self, panel, triggerCont, panelAlign):
        l, t, w, h = triggerCont.GetAbsolute()
        if panelAlign == neocomCommon.PANEL_SHOWABOVE:
            panel.left = l
            panel.top = t - panel.height
            if panel.left + panel.width > uicore.desktop.width:
                panel.left = l - panel.width + w
        elif panelAlign == neocomCommon.PANEL_SHOWONSIDE:
            if self.neocom.align == uiconst.TOLEFT:
                panel.left = l + w
            else:
                panel.left = l - panel.width
            panel.top = t
            if panel.top + panel.height > uicore.desktop.height - self.neocom.height:
                panel.top = t - panel.height + h
            if panel.left + panel.width > uicore.desktop.width:
                panel.left = l - panel.width
        dw = uicore.desktop.width
        dh = uicore.desktop.height
        if panel.top < 0:
            panel.top = 0
        elif panel.top + panel.height > dh:
            panel.top = dh - panel.height
        if panel.left < 0:
            panel.left = 0
        elif panel.left + panel.width > dw:
            panel.left = dw - panel.width

    def IsSomePanelOpen(self):
        return len(self.currPanels) > 0

    def OnGlobalMouseDown(self, cont, *args):
        if hasattr(cont, 'ToggleNeocomPanel'):
            return True
        if not isinstance(cont, neocomPanelEntries.PanelEntryBase):
            sm.ScatterEvent('OnNeocomPanelsClosed')
            self.CloseAllPanels()
            return False
        return True

    def CloseAllPanels(self):
        for panel in self.currPanels:
            panel.Close()

        self.currPanels = []

    def ClosePanel(self, panel):
        self.currPanels.remove(panel)
        panel.Close()

    def CloseChildrenPanels(self, btnData):
        toRemove = []
        for panel in self.currPanels:
            if panel.btnData and panel.btnData.IsDescendantOf(btnData):
                toRemove.append(panel)

        for panel in toRemove:
            panel.Close()
            self.currPanels.remove(panel)

    def ToggleEveMenu(self):
        if self.eveMenu and not self.eveMenu.destroyed:
            self.CloseAllPanels()
            self.eveMenu = None
        else:
            self.ShowEveMenu()

    def ShowEveMenu(self):
        self.neocom.UnhideNeocom(sleep=True)
        self.eveMenu = self.ShowPanel(self.neocom, PanelEveMenu, neocomCommon.PANEL_SHOWONSIDE, parent=uicore.layer.abovemain, btnData=self.eveMenuBtnData)
        sm.ScatterEvent('OnEveMenuShown')
        return self.eveMenu

    def GetSideOffset(self):
        width = settings.user.windows.Get('neocomWidth', Neocom.default_width)
        align = settings.char.ui.Get('neocomAlign', Neocom.default_align)
        if align == uiconst.TOLEFT:
            return (width, 0)
        else:
            return (0, width)

    def GetUIObjectByID(self, wndID):
        if not self.neocom:
            return
        if wndID == 'charactersheet':
            return self.neocom.charSheetBtn
        if wndID == 'skillTrainingCont':
            return self.neocom.skillTrainingCont
        for btnData in (self.btnData, self.scopeSpecificBtnData):
            if btnData:
                node = btnData.GetBtnDataByTypeAndID(None, wndID, recursive=True)
                if node:
                    if node.btnUI.destroyed:
                        return
                    return node.btnUI

        node = self.eveMenuBtnData.GetBtnDataByTypeAndID(None, wndID, recursive=True)
        if node:
            return self.neocom.eveMenuBtn

    def IsButtonVisible(self, wndID):
        for btnData in (self.btnData, self.scopeSpecificBtnData):
            if btnData is None:
                continue
            node = btnData.GetBtnDataByTypeAndID(None, wndID)
            if node:
                return True

        return False

    def OnButtonDragEnter(self, btnData, dragBtnData, *args):
        if not self.IsValidDropData(dragBtnData):
            return
        btns = self.GetButtonData()
        if btnData in btns:
            index = btns.index(btnData)
        else:
            index = len(btns)
        self.neocom.ShowDropIndicatorLine(index)

    def OnButtonDragExit(self, *args):
        self.neocom.HideDropIndicatorLine()

    def OnBtnDataDropped(self, btnData, index = None):
        if not self.IsValidDropData(btnData):
            return
        oldHeadNode = btnData.GetHeadNode()
        oldBtnData = self.btnData.GetBtnDataByGUID(btnData.wndCls, recursive=False)
        if btnData.btnType == neocomCommon.BTNTYPE_GROUP and oldHeadNode != self.btnData.GetHeadNode():
            toRemove = []
            for child in btnData.children:
                btnDataFound = self.btnData.GetBtnDataByGUID(child.wndCls, recursive=True)
                if btnDataFound:
                    toRemove.append(child)
                else:
                    child.isRemovable = True

            for child in toRemove:
                btnData.RemoveChild(child)

        btnData.MoveTo(self.btnData, index)
        if oldBtnData and oldBtnData != btnData:
            for child in oldBtnData.children:
                child.parent = btnData

            btnData.SetActive()
            oldBtnData.Remove()
        if oldHeadNode == self.eveMenuBtnData:
            self.ResetEveMenuBtnData()
            btnData.isRemovable = True

    def IsValidDropData(self, btnData):
        if not btnData:
            return False
        if isinstance(btnData, collections.Iterable):
            btnData = btnData[0]
        if not isinstance(btnData, BtnDataNode):
            return False
        if btnData.GetHeadNode() != self.btnData.GetHeadNode():
            if btnData.btnType == neocomCommon.BTNTYPE_GROUP:
                if self.btnData.GetBtnDataByTypeAndID(neocomCommon.BTNTYPE_GROUP, btnData.id, recursive=True):
                    return False
            else:
                foundBtnData = self.btnData.GetBtnDataByGUID(btnData.wndCls, recursive=True)
                if foundBtnData and foundBtnData.btnType != neocomCommon.BTNTYPE_WINDOW:
                    return False
        return True

    def GetMenu(self):
        m = [(localization.GetByLabel('UI/Neocom/CreateNewGroup'), self.AddNewGroup), None]
        if self.neocom.IsSizeLocked():
            m.append((uiutil.MenuLabel('UI/Neocom/UnlockNeocom'), self.neocom.SetSizeLocked, (False,)))
        else:
            m.append((uiutil.MenuLabel('UI/Neocom/LockNeocom'), self.neocom.SetSizeLocked, (True,)))
        if self.neocom.IsAutoHideActive():
            m.append((uiutil.MenuLabel('UI/Neocom/AutohideOff'), self.neocom.SetAutoHideOff))
        else:
            m.append((uiutil.MenuLabel('UI/Neocom/AutohideOn'), self.neocom.SetAutoHideOn))
        if self.neocom.align == uiconst.TOLEFT:
            m.append((uiutil.MenuLabel('UI/Neocom/AlignRight'), self.neocom.SetAlignRight))
        else:
            m.append((uiutil.MenuLabel('UI/Neocom/AlignLeft'), self.neocom.SetAlignLeft))
        if self.IsBlinkingEnabled():
            m.append((uiutil.MenuLabel('UI/Neocom/ConfigBlinkOff'), self.SetBlinkingOff))
        else:
            m.append((uiutil.MenuLabel('UI/Neocom/ConfigBlinkOn'), self.SetBlinkingOn))
        m.append((uiutil.MenuLabel('UI/Neocom/ResetButtons'), self.ResetButtons))
        if eve.session.role & service.ROLEMASK_ELEVATEDPLAYER:
            m.extend([None, ('Reload Insider', sm.StartService('insider').Reload), ('Toggle Insider', lambda : sm.StartService('insider').Toggle(forceShow=True))])
        return m

    def AddNewGroup(self):
        wnd = NeocomGroupNamePopup.Open()
        ret = wnd.ShowModal()
        if ret in (uiconst.ID_CLOSE, uiconst.ID_CANCEL):
            return
        BtnDataNodeGroup(parent=self.btnData, children=[], iconPath=neocomCommon.ICONPATH_GROUP, label=ret.label or localization.GetByLabel('UI/Neocom/ButtonGroup'), id='group_%s' % ret.label, btnType=neocomCommon.BTNTYPE_GROUP, labelAbbrev=ret.labelAbbrev)

    def EditGroup(self, btnData):
        wnd = NeocomGroupNamePopup.Open(groupName=btnData.label, groupAbbrev=btnData.labelAbbrev)
        ret = wnd.ShowModal()
        if ret in (uiconst.ID_CLOSE, uiconst.ID_CANCEL):
            return
        btnData.label = ret.label or localization.GetByLabel('UI/Neocom/ButtonGroup')
        btnData.labelAbbrev = ret.labelAbbrev
        btnData.Persist()

    def SetBlinkingOn(self):
        settings.char.windows.Set('neoblink', True)

    def SetBlinkingOff(self):
        settings.char.windows.Set('neoblink', False)
        self.BlinkStopAll()

    def BlinkStopAll(self):
        self.eveMenuBtnData.SetBlinkingOff()
        self.btnData.SetBlinkingOff()
        self.neocom.charSheetBtn.DisableBlink()

    def IsBlinkingEnabled(self):
        return settings.char.windows.Get('neoblink', True)

    def GetMenuForBtnData(self, btnData):
        return []

    def GetSidePanelSideOffset(self):
        return uicore.layer.sidePanels.GetSideOffset()


class BtnDataNode(util.KeyVal):
    __guid__ = 'neocom.BtnDataNode'
    __notifyevents__ = []
    persistChildren = True

    def __init__(self, parent = None, children = None, iconPath = None, label = None, id = None, btnType = None, isRemovable = True, isDraggable = True, isActive = False, isBlinking = False, labelAbbrev = None, wndCls = None, **kw):
        sm.RegisterNotify(self)
        self._parent = parent
        self.iconPath = iconPath
        self._children = children or []
        self.label = label
        self.labelAbbrev = labelAbbrev
        self.btnType = btnType
        self.btnUI = None
        self.isRemovable = isRemovable
        self.isDraggable = isDraggable
        self.isActive = isActive
        self.isBlinking = isBlinking
        self.blinkHint = ''
        self.blinkEndThread = None
        self.id = id
        self.guid = None
        self.cmdName = None
        self.wndCls = wndCls
        if not iconPath and wndCls:
            self.iconPath = wndCls.default_iconNum
        for attrname, val in kw.iteritems():
            setattr(self, attrname, val)

        if parent:
            parent._AddChild(self)

    def _AddChild(self, child):
        self._children.append(child)
        self.CheckContinueBlinking()
        if self.persistChildren:
            self.Persist()

    def GetChildren(self):
        return self._children

    children = property(GetChildren)

    def GetParent(self):
        return self._parent

    def SetParent(self, parent):
        self.parent._children.remove(self)
        self.parent.CheckContinueBlinking()
        self._parent = parent
        self.Persist()

    parent = property(GetParent, SetParent)

    def __repr__(self):
        return '<BtnDataNode: %s - %s children>' % (repr(self.label), len(self._children))

    def Persist(self, scatterEvent = True, fromChild = False):
        if fromChild and not self.persistChildren:
            return
        self.parent.Persist(scatterEvent, fromChild=True)

    def GetRawData(self):
        return util.KeyVal(btnType=self.btnType, id=self.id, iconPath=self.iconPath, children=self._GetRawChildren())

    def _GetRawChildren(self):
        rawChildren = None
        if self._children:
            rawChildren = []
            if self.persistChildren:
                for btnData in self._children:
                    if btnData.btnType not in NOTPERSISTED_BTNTYPES:
                        rawChildren.append(btnData.GetRawData())

        return rawChildren

    def SwitchWith(self, other):
        if other.parent != self.parent:
            return
        lst = self.parent._children
        indexSelf = lst.index(self)
        indexOther = lst.index(other)
        lst.insert(indexOther, lst.pop(indexSelf))
        self.Persist(scatterEvent=False)

    def GetIndex(self):
        lst = self.parent._children
        return lst.index(self)

    def GetBtnDataByTypeAndID(self, btnType, id, recursive = False):
        for btnData in self._children:
            if btnType is None or btnData.btnType == btnType:
                if btnData.id == id:
                    return btnData
            if recursive:
                subBtnData = btnData.GetBtnDataByTypeAndID(btnType, id, True)
                if subBtnData:
                    return subBtnData

    def GetBtnDataByGUID(self, guid, recursive = False):
        if guid is None:
            return
        for btnData in self._children:
            if getattr(btnData, 'guid', None) == guid:
                return btnData
            if recursive:
                subBtnData = btnData.GetBtnDataByGUID(guid, True)
                if subBtnData:
                    return subBtnData

    def RemoveChild(self, btnData):
        btnData.parent = None
        self._children.remove(btnData)
        if self.persistChildren:
            self.Persist()

    def MoveTo(self, newParent, index = None):
        if newParent == self:
            return
        if not self.IsRemovable():
            return
        self.parent._children.remove(self)
        if index is None:
            newParent._children.append(self)
        else:
            newParent._children.insert(index, self)
        oldParent = self.parent
        self.parent = newParent
        oldParent.CheckContinueBlinking()
        self.Persist()
        oldParent.Persist()

    def Remove(self):
        self.parent.RemoveChild(self)

    def IsRemovable(self):
        if self.isRemovable:
            for btnData in self._children:
                if not btnData.IsRemovable():
                    return False

        return True

    def GetHeadNode(self):
        return self.parent.GetHeadNode()

    def IsDescendantOf(self, btnData):
        return self.parent._IsDescendantOf(btnData)

    def _IsDescendantOf(self, btnData):
        if self == btnData:
            return True
        return self.parent._IsDescendantOf(btnData)

    def SetBlinkingOn(self, hint = '', numBlinks = None):
        self.isBlinking = True
        self.blinkHint = hint
        if numBlinks:
            uthread.new(self._StopBlinkThread, numBlinks)
        if self.parent:
            self.parent.SetBlinkingOn(hint)
        sm.ScatterEvent('OnNeocomBlinkingChanged')

    def _StopBlinkThread(self, numBlinks):
        blue.synchro.SleepWallclock(numBlinks * neocomCommon.BLINK_INTERVAL)
        self.SetBlinkingOff()

    def SetBlinkingOff(self):
        self._SetBlinkingOff()
        if self.parent:
            self.parent.CheckContinueBlinking()
        sm.ScatterEvent('OnNeocomBlinkingChanged')

    def _SetBlinkingOff(self):
        self.isBlinking = False
        self.blinkHint = ''
        for btnData in self._children:
            btnData._SetBlinkingOff()

    def CheckContinueBlinking(self):
        for btnData in self._children:
            if btnData.isBlinking:
                sm.ScatterEvent('OnNeocomBlinkingChanged')
                self.isBlinking = True
                return

        self.isBlinking = False
        if self.parent:
            self.parent.CheckContinueBlinking()
        else:
            sm.ScatterEvent('OnNeocomBlinkingChanged')

    def SetActive(self):
        self.isActive = True
        if hasattr(self.btnUI, 'CheckIfActive'):
            self.btnUI.CheckIfActive()

    def SetInactive(self):
        self.isActive = False
        if hasattr(self.btnUI, 'CheckIfActive'):
            self.btnUI.CheckIfActive()

    def GetHint(self, label = None):
        hintStr = label or self.label
        if self.btnType == neocomCommon.BTNTYPE_CMD:
            cmd = uicore.cmd.commandMap.GetCommandByName(self.cmdName)
            shortcutStr = cmd.GetShortcutAsString()
            if shortcutStr:
                hintStr += ' [%s]' % shortcutStr
            if self.blinkHint:
                hintStr += '<br>%s' % self.blinkHint
        return hintStr

    def GetMenu(self):
        m = []
        if self.isRemovable and not self.isActive:
            m.append((localization.GetByLabel('UI/Commands/Remove'), self.Remove))
        m += sm.GetService('neocom').GetMenuForBtnData(self)
        return m

    def IsButtonInScope(self):
        if self.id == 'twitch' and blue.sysinfo.isTransgaming:
            return False
        if self.id == 'map_beta' and not IsMapBetaEnabled():
            return False
        if self.id == 'map' and IsMapBetaEnabled():
            return False
        if self.id in ('corpHangar', 'corpDeliveriesHangar') and util.IsNPCCorporation(session.corpid):
            return False
        if self.id == 'corpHangar' and not self._HasCorpOffice():
            return False
        if self.id == 'tutorial' and not sm.GetService('experimentClientSvc').IsTutorialEnabled():
            return False
        if self.id == 'opportunities' and not sm.GetService('experimentClientSvc').OpportunitiesEnabled():
            return False
        if self.wndCls:
            scope = self.wndCls.default_scope
            if not scope or scope == 'station_inflight':
                return True
            if session.structureid and scope in ('structure', 'station'):
                return True
            if session.stationid2 and scope != 'station':
                return False
            if session.solarsystemid and scope != 'space':
                return False
        return True

    def GetButtonsInScope(self):
        return [ btnData for btnData in self.children if btnData.IsButtonInScope() ]

    def _HasCorpOffice(self):
        if session.structureid:
            if sm.GetService('structureOffices').HasOffice():
                return True
        if sm.GetService('corp').GetOffice():
            return True
        return False


class BtnDataHeadNode(BtnDataNode):
    __guid__ = 'neocom.BtnDataHeadNode'

    def __init__(self, id = None, rawBtnData = None, isRemovable = True, persistChildren = True):
        self.id = id
        self._parent = None
        self._persistThread = None
        rawBtnData = rawBtnData or []
        self._children = []
        self._GetButtonDataFromnRawData(self, rawBtnData, isRemovable)
        self.isBlinking = False
        self.persistChildren = persistChildren

    def __repr__(self):
        return '<BtnDataHeadNode: %s children>' % len(self._children)

    def Persist(self, scatterEvent = True, fromChild = False):
        if not self._persistThread:
            self._persistThread = uthread.new(self._Persist, scatterEvent)

    def _Persist(self, scatterEvent):
        if self.persistChildren:
            savedData = []
            for btnData in self._children:
                if btnData.btnType not in NOTPERSISTED_BTNTYPES:
                    savedData.append(btnData.GetRawData())

            settings.char.ui.Set('%sButtonRawData' % self.id, savedData)
        if scatterEvent:
            sm.ScatterEvent('OnHeadNodeChanged', self.id)
        self._persistThread = None

    def _GetButtonDataFromnRawData(self, parent, rawData, isRemovable):
        nodes = []
        for data in rawData:
            data = ConvertOldTypeOfRawData(data)
            nodeClass = NODECLASS_BY_TYPE.get(data.btnType, BtnDataNode)
            btnDataRaw = BTNDATARAW_BY_ID.get(data.id)
            if btnDataRaw:
                label = None
                if btnDataRaw.cmdName:
                    cmd = uicore.cmd.commandMap.GetCommandByName(btnDataRaw.cmdName)
                    if cmd:
                        label = cmd.GetName()
                if label is None:
                    if data.Get('label', None):
                        label = data.label
                    else:
                        label = localization.GetByLabel(btnDataRaw.label)
                iconPath = btnDataRaw.iconPath
                cmdName = btnDataRaw.cmdName
                wndCls = btnDataRaw.wndCls
                guid = wndCls
            elif data.btnType == neocomCommon.BTNTYPE_GROUP:
                label = data.label
                iconPath = neocomCommon.ICONPATH_GROUP
                guid = data.id
                cmdName = None
                wndCls = None
            else:
                continue
            btnData = nodeClass(parent=parent, iconPath=iconPath, id=data.id, guid=guid, label=label, btnType=data.btnType, cmdName=cmdName, isRemovable=isRemovable, labelAbbrev=data.Get('labelAbbrev', None), wndCls=wndCls)
            if data.children:
                self._GetButtonDataFromnRawData(btnData, data.children, isRemovable)
            nodes.append(btnData)

        return nodes

    def GetHeadNode(self):
        return self

    def IsDescendantOf(self, btnData):
        return False

    def _IsDescendantOf(self, btnData):
        return btnData == self


class BtnDataNodeDynamic(BtnDataNode):
    __guid__ = 'neocom.BtnDataNodeDynamic'
    persistChildren = False

    def GetDataList(self):
        return []

    def GetNodeFromData(self, data, parent):
        pass

    def _AddChild(self, child):
        pass

    def ProcessNeocomBlinkPulse(self):
        pass

    def CheckContinueBlinking(self):
        pass

    def RemoveChild(self, btnData):
        pass

    def GetChildren(self):
        dataList = self.GetDataList()
        return self._GetChildren(dataList, self)

    def GetPanelEntryHeight(self):
        return 25

    def _GetChildren(self, dataList, parent = None):
        children = []
        entryHeight = self.GetPanelEntryHeight()
        maxEntries = uicore.desktop.height / entryHeight - 1
        for data in dataList[:maxEntries]:
            btnData = self.GetNodeFromData(data, parent)
            children.append(btnData)

        overflow = dataList[maxEntries:]
        if overflow:
            overflowBtnData = BtnDataNode(parent=parent, iconPath=neocomCommon.ICONPATH_GROUP, label=localization.GetByLabel('UI/Neocom/OverflowButtonsLabel', numButtons=len(overflow)), btnType=neocomCommon.BTNTYPE_GROUP, panelEntryHeight=entryHeight, isRemovable=False, isDraggable=False)
            children.append(overflowBtnData)
            self._GetChildren(dataList[maxEntries:], overflowBtnData)
        return children

    children = property(GetChildren)


class BtnDataNodeGroup(BtnDataNode):
    __guid__ = 'neocom.BtnDataNodeGroup'

    def GetMenu(self):
        if self.GetHeadNode() == sm.GetService('neocom').eveMenuBtnData:
            return
        m = []
        if self.IsRemovable():
            m.append((uiutil.MenuLabel('UI/Commands/Remove'), self.Remove, ()))
            m.append((localization.GetByLabel('UI/Neocom/Edit'), sm.GetService('neocom').EditGroup, (self,)))
        return m

    def GetRawData(self):
        return util.KeyVal(btnType=self.btnType, id=self.id, iconPath=self.iconPath, children=self._GetRawChildren(), label=self.label, labelAbbrev=self.labelAbbrev)


class BtnDataNodeBookmarks(BtnDataNodeDynamic):
    __guid__ = 'neocom.BtnDataNodeBookmarks'

    def GetDataList(self):
        bookmarkData = sm.GetService('sites').GetBookmarks()[:]
        bookmarkData.insert(0, util.KeyVal(url='home', name=localization.GetByLabel('UI/Neocom/Homepage')))
        return bookmarkData

    def GetNodeFromData(self, bookmark, parent):
        return BtnDataNode(parent=parent, children=None, iconPath=neocomCommon.ICONPATH_BOOKMARKS, label=bookmark.name, id=bookmark.name, btnType=neocomCommon.BTNTYPE_BOOKMARK, bookmark=bookmark, isRemovable=False, isDraggable=False)


class BtnDataNodeChat(BtnDataNodeDynamic):
    __guid__ = 'neocom.BtnDataNodeChat'
    __notifyevents__ = ['ProcessNeocomBlinkPulse']

    def GetMenu(self):
        return [(localization.GetByLabel('UI/Commands/OpenChannels'), uicore.cmd.OpenChannels, [])]

    def ProcessNeocomBlinkPulse(self):
        self.isBlinking = False
        if sm.GetService('neocom').IsBlinkingEnabled():
            for wnd in self._GetOpenChatWindows():
                if getattr(wnd, 'isBlinking', False):
                    if wnd.InStack() and wnd.GetStack().display:
                        continue
                    self.isBlinking = True
                    return

    def _GetOpenChatWindows(self):
        return [ wnd for wnd in uicore.registry.GetWindows() if wnd.__class__ == Channel ]

    def GetDataList(self):

        def GetKey(wnd):
            priority = ('chatchannel_solarsystemid2', 'chatchannel_corpid', 'chatchannel_allianceid', 'chatchannel_fleetid', 'chatchannel_squadid', 'chatchannel_wingid')
            if wnd.name in priority:
                return priority.index(wnd.name)
            else:
                return wnd.GetCaption()

        sortedData = sorted(self._GetOpenChatWindows(), key=GetKey)
        data = uiutil.Bunch(addChatChannelWnd=1)
        sortedData.insert(0, data)
        return sortedData

    def GetNodeFromData(self, wnd, parent):
        if getattr(wnd, 'addChatChannelWnd', False):
            cmd = uicore.cmd.commandMap.GetCommandByName(BTNDATARAW_BY_ID['chatchannels'].cmdName)
            return BtnDataNode(parent=parent, children=None, iconPath=Channels.default_iconNum, id='chatchannels', guid=None, btnType=neocomCommon.BTNTYPE_CMD, cmdName=BTNDATARAW_BY_ID['chatchannels'].cmdName, isRemovable=False, isDraggable=False, label=cmd.GetName())
        else:
            return BtnDataNode(parent=parent, iconPath=neocomCommon.ICONPATH_CHAT, label=wnd.GetCaption(), id=wnd.windowID, btnType=neocomCommon.BTNTYPE_CHATCHANNEL, wnd=wnd, isRemovable=False, isDraggable=False, isBlinking=getattr(wnd, 'isBlinking', False))


NODECLASS_BY_TYPE = {neocomCommon.BTNTYPE_CHAT: BtnDataNodeChat,
 neocomCommon.BTNTYPE_BOOKMARKS: BtnDataNodeBookmarks,
 neocomCommon.BTNTYPE_GROUP: BtnDataNodeGroup}

class NeocomGroupNamePopup(uicontrols.Window):
    default_windowID = 'NeocomGroupNamePopup'
    default_topParentHeight = 0
    default_fixedWidth = 180
    default_fixedHeight = 130
    default_caption = 'UI/Neocom/NeocomGroup'

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        self.btnData = attributes.get('btnData', None)
        groupName = attributes.get('groupName', '')
        groupAbbrev = attributes.get('groupAbbrev', '')
        self.sr.main.padLeft = 6
        self.sr.main.padRight = 6
        self.sr.main.padBottom = 4
        self.labelEdit = uicontrols.SinglelineEdit(name='labelEdit', label=localization.GetByLabel('UI/Neocom/NeocomGroupName'), parent=self.sr.main, align=uiconst.TOTOP, padTop=20, setvalue=groupName, OnReturn=self.Confirm)
        self.labelEdit.SetMaxLength(30)
        self.labelAbbrevEdit = uicontrols.SinglelineEdit(name='labelAbbrevEdit', label=localization.GetByLabel('UI/Neocom/NeocomGroupNameAbbrev'), parent=self.sr.main, align=uiconst.TOTOP, padTop=20, setvalue=groupAbbrev, OnReturn=self.Confirm)
        self.labelAbbrevEdit.SetMaxLength(2)
        btns = uicontrols.ButtonGroup(parent=self.sr.main, line=False, btns=((localization.GetByLabel('UI/Common/Confirm'), self.Confirm, ()), (localization.GetByLabel('UI/Commands/Cancel'), self.Close, ())))

    def Confirm(self, *args):
        kv = util.KeyVal(label=self.labelEdit.GetValue(), labelAbbrev=self.labelAbbrevEdit.GetValue())
        self.SetModalResult(kv)
