#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\dockedUI\lobbyWnd.py
import collections
from carbon.common.script.util.format import FmtAmt, CaseFoldCompare
from carbonui.control.basicDynamicScroll import BasicDynamicScroll
from carbonui.primitives.container import Container
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.util.sortUtil import SortListOfTuples
from carbonui.util.various_unsorted import NiceFilter
from eve.client.script.ui.control.buttons import ToggleButtonGroup, Button
from eve.client.script.ui.control.eveIcon import CheckCorpID, GetLogoIcon
from eve.client.script.ui.control.eveLabel import CaptionLabel, EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.eveWindow import Window
import carbonui.const as uiconst
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.tabGroup import TabGroup
from eve.client.script.ui.control.utilMenu import UtilMenu
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.shared.dockedUI.counterBox import CounterBox
from eve.client.script.ui.shared.dockedUI.inControlCont import ConfirmTakeControl
from eve.client.script.ui.shared.dockedUI.lobbyToggleButtonGroupButton import LobbyToggleButtonGroupButton
from eve.client.script.ui.shared.dockedUI.modeBtn import DockedModeBtn, UndockBtn, ControlBtn
from eve.client.script.ui.shared.dockedUI.officeEntry import OfficeEntry
from eve.client.script.ui.shared.dockedUI.serivceBtn import StationServiceBtn
from eve.client.script.ui.station import stationServiceConst
from eve.common.script.sys.eveCfg import IsDockedInStructure
from localization import GetByLabel
from eve.client.script.ui.control.entries import Get as GetListEntry
from eve.client.script.ui.shared.inventory.invWindow import Inventory as InventoryWindow
import uthread
from utillib import KeyVal
import blue
import telemetry
MAX_CORP_DESC_LENGTH = 140
MAX_CORP_DESC_LINES = 1
BIGBUTTONSIZE = 48
SMALLBUTTONSIZE = 32
BUTTONGAP = 4
AGENTSPANEL = 'agentsPanel'
GUESTSPANEL = 'guestsPanel'
OFFICESPANEL = 'officesPanel'
INVENTORYPANEL = 'inventoryPanel'

class LobbyWnd(Window):
    __guid__ = 'form.LobbyWnd'
    __notifyevents__ = ['OnCharNowInStation',
     'OnCharNoLongerInStation',
     'OnCharacterEnteredStructure',
     'OnCharacterLeftStructure',
     'OnProcessStationServiceItemChange',
     'OnAgentMissionChange',
     'OnStandingSet',
     'OnCorporationChanged',
     'OnCorporationMemberChanged',
     'OnPrimaryViewChanged',
     'OnSetDevice',
     'OnStructureServiceUpdated']
    default_windowID = 'lobbyWnd'
    default_top = 16
    default_width = 223
    default_captionLabelPath = 'UI/Station/StationServices'
    default_pinned = True
    undockCont = None
    undock_button_is_locked = False
    selectedGroupButtonID = None

    @staticmethod
    def default_height(*args):
        return uicore.desktop.height - 100

    @staticmethod
    def default_left(*args):
        return uicore.desktop.width - LobbyWnd.default_width - 16

    def OnPrimaryViewChanged(self, oldViewInfo, newViewInfo):
        self.UpdateDockedModeBtn(newViewInfo.name)

    def OnSetDevice(self):
        bottom = self.top + self.height
        if bottom > uicore.desktop.height:
            self.height = max(self.default_minSize[1], uicore.desktop.height - self.top)
        right = self.left + self.width
        if right > uicore.desktop.width:
            self.width = max(self.default_minSize[0], uicore.desktop.width - self.left)

    def _SetDefaultMinSize(self):

        def GetMinSize(btnSize, numInRow, padding):
            return btnSize + (btnSize + BUTTONGAP) * numInRow + padding

        btnSize = self.GetServiceBtnSize()
        if not settings.user.ui.Get('stationservicebtns', 1):
            minWidth = GetMinSize(btnSize, 3, 14)
            minHeight = 495
        else:
            minWidth = GetMinSize(btnSize, 5, 10)
            minHeight = 470
        self.default_minSize = (minWidth, minHeight)

    def ApplyAttributes(self, attributes):
        self.viewState = sm.GetService('viewState')
        self.scope = 'station'
        self.userType = settings.user.ui.Get('guestCondensedUserList', False)
        self._SetDefaultMinSize()
        Window.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.SetGuestEntryType()
        self.guestScroll = None
        self.SetWndIcon(None)
        self.HideHeader()
        self.MakeUnKillable()
        self.MakeUnstackable()
        self.SetTopparentHeight(0)
        self.sr.main.clipChildren = True
        self.BuildTopSection()
        self._AddStationServices()
        btnGroup = self._AddPanelToggleBtnCont()
        self._AddGuestPanel()
        self._AddAgentPanel()
        self._AddOfficePanel()
        self._AddToggleBtns()
        activePanel = settings.user.ui.Get('stationsLobbyTabs', AGENTSPANEL)
        if settings.char.windows.Get('dockshipsanditems', 0):
            self._AddInventoryPanel(btnGroup)
        elif activePanel == INVENTORYPANEL:
            activePanel = AGENTSPANEL
        btnGroup.SelectByID(activePanel)
        self._SetCorrectViewState()
        self.LoadOwnerInfo()
        self.LoadServiceButtons()
        if self.destroyed:
            return
        sm.RegisterNotify(self)
        self.UpdateGuestTabText()

    def BuildTopSection(self):
        self.corpLogoParent = Container(name='corpLogoParent', align=uiconst.TOTOP, height=160, parent=self.sr.main)
        self.corpName = CaptionLabel(parent=self.sr.main, align=uiconst.TOTOP, name='corpName', uppercase=False)
        self.undockparent = Container(name='undockparent', align=uiconst.TOTOP, height=86, parent=self.sr.main)
        self.AddDockedModeButton()
        self.AddControlButton()
        self.AddUndockButton()

    def _AddStationServices(self):
        EveLabelMedium(text=GetByLabel('UI/Station/StationServices'), align=uiconst.TOTOP, parent=self.sr.main, bold=True, padding=(6, 6, 6, 0))
        self.serviceButtons = FlowContainer(name='serviceButtons', align=uiconst.TOTOP, parent=self.sr.main, contentSpacing=(BUTTONGAP, BUTTONGAP), padding=(6, 6, 3, 6))

    def _AddGuestPanel(self):
        self.guestsPanel = Container(name=GUESTSPANEL, parent=self.sr.main, padding=const.defaultPadding)
        self.quickFilter = QuickFilterEdit(name='quickFilterEdit', parent=self.guestsPanel)
        self.quickFilter.ReloadFunction = lambda : self.ShowGuests()
        self.guestScroll = BasicDynamicScroll(parent=self.guestsPanel, padTop=const.defaultPadding + self.quickFilter.height)
        guestSettingsMenu = UtilMenu(menuAlign=uiconst.TOPRIGHT, parent=self.guestsPanel, align=uiconst.TOPRIGHT, GetUtilMenu=self.SettingMenu, texturePath='res:/UI/Texture/SettingsCogwheel.png', width=18, height=18, iconSize=18)

    def _AddAgentPanel(self):
        self.agentsPanel = Container(name=AGENTSPANEL, parent=self.sr.main, padding=const.defaultPadding)
        self.agentFinderBtn = Button(label=GetByLabel('UI/AgentFinder/AgentFinder'), parent=self.agentsPanel, align=uiconst.CENTERTOP, func=uicore.cmd.OpenAgentFinder)
        self.agentScroll = Scroll(parent=self.agentsPanel, padTop=const.defaultPadding + self.agentFinderBtn.height)

    def _AddPanelToggleBtnCont(self):
        btnGroup = ToggleButtonGroup(name='btnGroup', parent=self.sr.main, align=uiconst.TOTOP, height=32, padding=6, idx=-1, callback=self.OnButtonGroupSelection, autoHeight=True)
        self.mainButtonGroup = btnGroup
        return btnGroup

    def _AddToggleBtns(self):
        btnGroup = self.mainButtonGroup
        agentsButton = btnGroup.AddButton(AGENTSPANEL, '<center>' + GetByLabel('UI/Station/Lobby/Agents'), self.agentsPanel, btnClass=LobbyToggleButtonGroupButton, hint=GetByLabel('Tooltips/StationServices/AgentsTab_descrtiption'))
        agentsButton.name = 'stationInformationTabAgents'
        guestsButton = btnGroup.AddButton(GUESTSPANEL, '<center>' + GetByLabel('UI/Station/Lobby/Guests'), self.guestsPanel, btnClass=LobbyToggleButtonGroupButton, hint=GetByLabel('Tooltips/StationServices/GuestsTab_description'))
        guestsButton.counter = CounterBox(parent=guestsButton, align=uiconst.TOPRIGHT, left=2, top=-5)
        self.guestsButton = guestsButton
        btnGroup.AddButton(OFFICESPANEL, '<center>' + GetByLabel('UI/Station/Lobby/Offices'), self.officesPanel, btnClass=LobbyToggleButtonGroupButton, hint=GetByLabel('Tooltips/StationServices/OfficesTab_description'))

    def _AddOfficePanel(self):
        self.officesPanel = Container(name=OFFICESPANEL, parent=self.sr.main, padding=const.defaultPadding)
        self.officesButtons = FlowContainer(name='officesButtons', align=uiconst.TOTOP, parent=self.officesPanel, contentSpacing=(4, 4), centerContent=True)
        self.officesScroll = Scroll(parent=self.officesPanel, padTop=const.defaultPadding)

    def _AddInventoryPanel(self, btnGroup):
        self.inventoryPanel = Container(name=INVENTORYPANEL, parent=self.sr.main)
        self.sr.shipsContainer = Container(parent=self.inventoryPanel, state=uiconst.UI_HIDDEN, padding=const.defaultPadding)
        self.sr.itemsContainer = Container(parent=self.inventoryPanel, state=uiconst.UI_HIDDEN, padding=const.defaultPadding)
        tabs = [[GetByLabel('UI/Station/Ships'),
          self.sr.shipsContainer,
          self,
          'lobby_ships'], [GetByLabel('UI/Station/Items'),
          self.sr.itemsContainer,
          self,
          'lobby_items']]
        self.inventoryTabs = TabGroup(name='inventoryPanel', parent=self.inventoryPanel, idx=0)
        self.inventoryTabs.Startup(tabs, 'lobbyInventoryPanel', autoselecttab=True, UIIDPrefix='lobbyInventoryPanelTab')
        hint = '<b>%s</b><br>%s' % (GetByLabel('Tooltips/StationServices/Hangars'), GetByLabel('Tooltips/StationServices/Hangars_description'))
        self.invButton = btnGroup.AddButton(INVENTORYPANEL, '<center>' + GetByLabel('UI/Station/Lobby/Hangars'), self.inventoryPanel, btnClass=LobbyToggleButtonGroupButton, hint=hint)

    def LoadOwnerInfo(self):
        parent = self.corpLogoParent
        parent.Flush()
        corpID = self.controller.GetOwnerID()
        size = 128 if CheckCorpID(corpID) else 64
        logo = GetLogoIcon(itemID=corpID, parent=parent, acceptNone=False, state=uiconst.UI_DISABLED, pos=(0,
         8,
         size,
         size), align=uiconst.CENTERTOP)
        InfoIcon(typeID=const.typeCorporation, itemID=corpID, left=const.defaultPadding, top=20, align=uiconst.TOPRIGHT, parent=parent, idx=0)
        parent.height = logo.top + logo.height
        if CheckCorpID(corpID):
            self.corpName.display = False
        else:
            self.corpName.text = '<center>' + cfg.eveowners.Get(corpID).name
            self.corpName.display = True

    def GetServiceBtnSize(self):
        stationservicebtns = settings.user.ui.Get('stationservicebtns', 1)
        if stationservicebtns:
            return SMALLBUTTONSIZE
        else:
            return BIGBUTTONSIZE

    def LoadServiceButtons(self):
        parent = self.serviceButtons
        parent.Flush()
        haveServices = self.GetCurrentStationServices()
        btnsize = self.GetServiceBtnSize()
        for serviceInfo in reversed(haveServices):
            button = StationServiceBtn(parent=parent, pos=(0,
             0,
             btnsize,
             btnsize), name=serviceInfo.name, align=uiconst.NOALIGN, serviceInfo=serviceInfo, callback=self.OnSvcBtnClick, serviceStatus=GetByLabel('UI/Station/Lobby/Enabled'), serviceEnabled=True)
            self.SetServiceButtonState(button, serviceInfo.serviceID)
            button.LoadTooltipPanel = self.LoadServiceButtonTooltipPanel

    def ReloadServiceButtons(self):
        self.controller.GetServicesInStation()
        for icon in self.serviceButtons.children:
            self.SetServiceButtonState(icon, icon.serviceID)

    def SetServiceButtonState(self, button, serviceID):
        currentstate = self.controller.GetCurrentStateForService(serviceID)
        if currentstate is None:
            return
        self.controller.RemoveServiceFromCache(serviceID)
        if currentstate.isEnabled:
            button.EnableBtn()
        else:
            button.DisableBtn()

    def OnSvcBtnClick(self, btn, *args):
        self.CheckCanAccessService(btn.name)
        sm.GetService('station').LoadSvc(btn.name)

    def CheckCanAccessService(self, serviceName):
        serviceData = stationServiceConst.serviceDataByNameID.get(serviceName)
        if serviceData is None:
            return
        for stationServiceID in serviceData.maskServiceIDs:
            result = self.controller.PerformAndGetErrorForStandingCheck(stationServiceID)
            if result is not None:
                raise result

    def LoadServiceButtonTooltipPanel(self, tooltipPanel, tooltipOwner, *args):
        tooltipPanel.LoadGeneric3ColumnTemplate()
        command = uicore.cmd.commandMap.GetCommandByName(tooltipOwner.cmdStr)
        tooltipPanel.AddCommandTooltip(command)
        if not tooltipOwner.serviceEnabled:
            tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Station/Lobby/Disabled'), color=(1, 0, 0, 1), bold=True, colSpan=tooltipPanel.columns)

    def GetCurrentStationServices(self):
        return self.controller.GetServicesInStation()

    def _SetCorrectViewState(self):
        myDefaultView = 'hangar' if session.userid % 2 == 1 else 'station'
        curView = collections.namedtuple('FakeViewInfo', ['name'])(settings.user.ui.Get('defaultDockingView', myDefaultView))
        self.OnPrimaryViewChanged(curView, curView)

    def OnButtonGroupSelection(self, buttonID):
        settings.user.ui.Set('stationsLobbyTabs', buttonID)
        self.selectedGroupButtonID = buttonID
        if buttonID == AGENTSPANEL:
            self.ShowAgents()
        elif buttonID == GUESTSPANEL:
            self.ShowGuests()
        elif buttonID == OFFICESPANEL:
            self.ShowOffices()
        elif buttonID == INVENTORYPANEL:
            if not len(self.sr.shipsContainer.children):
                self.LayoutShipsAndItems()

    def SettingMenu(self, menuParent):
        showCompact = settings.user.ui.Get('guestCondensedUserList', False)
        menuParent.AddCheckBox(text=GetByLabel('UI/Chat/ShowCompactMemberList'), checked=bool(showCompact), callback=self.ChangeGuestEntryType)

    def ChangeGuestEntryType(self, *args):
        showCompact = settings.user.ui.Get('guestCondensedUserList', False)
        settings.user.ui.Set('guestCondensedUserList', not showCompact)
        self.SetGuestEntryType()
        self.ShowGuests()

    def SetGuestEntryType(self):
        if settings.user.ui.Get('guestCondensedUserList', False):
            self.userEntry = 'ChatUserSimple'
        else:
            self.userEntry = 'User'

    def _GetNumLobbyBtns(self):
        if self.controller.IsControlable():
            return 3
        else:
            return 2

    def AddControlButton(self):
        if not self.controller.IsControlable():
            return
        width = 1.0 / self._GetNumLobbyBtns()
        self.takeControlBtn = ControlBtn(parent=self.undockparent, name='dockedModeBtn', padding=3, callback=self.TakeControl, width=width)
        self.takeControlBtn.SetBtnLabel(GetByLabel('UI/Commands/TakeStructureControl'))
        if not self.controller.CanTakeControl():
            self.takeControlBtn.DisableBtn()

    def TakeControl(self, *args):
        charInControl = self.controller.GetCharInControl()
        if charInControl:
            ConfirmTakeControl.Open(controller=self.controller, charInControl=charInControl)
        else:
            self.controller.TakeControl()

    def AddDockedModeButton(self):
        width = 1.0 / self._GetNumLobbyBtns()
        self.dockedModeBtn = DockedModeBtn(parent=self.undockparent, name='dockedModeBtn', padding=3, callback=self.OnDockModeClicked, isMouseOverDisabledFunc=sm.GetService('station').PastUndockPointOfNoReturn(), width=width)
        self.UpdateDockedModeBtn()
        if self.controller.IsRestrictedByGraphicsSettings():
            self.dockedModeBtn.DisableBtn()
            textPath = self.controller.GetDisabledDockingModeHint()
            if textPath:
                self.dockedModeBtn.SetBtnHint(GetByLabel(textPath))
        else:
            self.dockedModeBtn.EnableBtn()

    def UpdateDockedModeBtn(self, viewName = None):
        textPath = self.controller.GetDockedModeTextPath(viewName)
        text = '<center>%s</center>' % GetByLabel(textPath)
        self.dockedModeBtn.SetBtnLabel(text)
        self.dockedModeBtn.AdjustBtnHeight()

    def OnDockModeClicked(self, *args):
        self.controller.ChangeDockedMode(self.viewState)

    def OnUndockClicked(self, *args):
        if self.controller.InProcessOfUndocking():
            return
        uthread.new(self.AttemptToUndock).context = 'UndockButtonThread'

    def AddUndockButton(self):
        width = 1.0 / self._GetNumLobbyBtns()
        self.undockBtn = UndockBtn(parent=self.undockparent, name='undockBtn', padding=3, callback=self.OnUndockClicked, width=width)
        self.UpdateUndockButton()
        self.undockBtn.AdjustBtnHeight()
        if self.undock_button_is_locked:
            self._DisableUndockButton()

    def UpdateUndockButton(self):
        if self.controller.IsExiting():
            text = GetByLabel('UI/Station/AbortUndock')
            self.LockDockedModeButton()
        else:
            text = GetByLabel('UI/Neocom/UndockBtn')
            self.UnlockDockedModeButton()
        self.undockBtn.SetBtnLabel('<center>%s</center>' % text)

    def LockUndockButton(self):
        self.undock_button_is_locked = True
        self._DisableUndockButton()

    def _DisableUndockButton(self):
        if self.undockBtn is not None:
            self.undockBtn.LockBtn()

    def UnlockUndockButton(self):
        self.undock_button_is_locked = False
        self._EnableUndockButton()

    def _EnableUndockButton(self):
        if self.undockBtn is not None:
            self.undockBtn.UnlockBtn()

    def LockDockedModeButton(self, *args):
        self.dockedModeBtn.LockBtn()

    def UnlockDockedModeButton(self, *args):
        self.dockedModeBtn.UnlockBtn()

    def SetUndockProgress(self, undockProgress):
        if undockProgress is None:
            self.UpdateUndockButton()
            return
        i = int(undockProgress * 3)
        if i < 3:
            self.UpdateUndockButton()
            self.undockBtn.AnimateArrow(arrowIdx=i)
        else:
            text = '<center>%s</center>' % GetByLabel('UI/Station/UndockingConfirmed')
            self.undockBtn.StartConfirmedAnimation()

    def UpdateGuestTabText(self):
        numGuests = len(self.controller.GetGuests())
        self.guestsButton.counter.text = numGuests

    def AttemptToUndock(self):
        exiting = self.controller.Undock()
        if exiting:
            self.LockDockedModeButton()

    def LayoutShipsAndItems(self):
        self.sr.itemsContainer.Flush()
        stationItemsClass, stationShipsClass = self.controller.GetStationItemsAndShipsClasses()
        itemID = self.controller.GetItemID()
        itemsContainer = stationItemsClass(name='stationItems', parent=self.sr.itemsContainer, showControls=True, state=uiconst.UI_NORMAL, itemID=itemID)
        self.sr.shipsContainer.Flush()
        shipsContainer = stationShipsClass(name='stationShips', parent=self.sr.shipsContainer, showControls=True, state=uiconst.UI_NORMAL, itemID=itemID)
        self.invButton.OnDropData = itemsContainer.OnDropData
        self.sr.itemsContainer.OnDropData = itemsContainer.OnDropData
        self.sr.shipsContainer.OnDropData = shipsContainer.OnDropData

    def ShowOffices(self):
        if self.selectedGroupButtonID != OFFICESPANEL:
            return
        self.LoadButtons()
        corpsWithOffices = self.controller.CorpsWithOffices()
        cfg.corptickernames.Prime([ c.corporationID for c in corpsWithOffices ])
        scrolllist = []
        for corp in corpsWithOffices:
            corpName = corp.corporationName
            data = KeyVal(corpName=corpName, corpID=corp.corporationID, corporation=corp)
            entry = GetListEntry(data=data, decoClass=OfficeEntry)
            scrolllist.append((corpName.lower(), entry))

        scrolllist = SortListOfTuples(scrolllist)
        numUnrentedOffices = self.controller.GetNumberOfUnrentedOffices()
        if numUnrentedOffices is not None:
            availOfficesLabel = GetByLabel('UI/Station/Lobby/NumAvailableOffices', numOffices=numUnrentedOffices)
            scrolllist.insert(0, GetListEntry('Header', {'label': availOfficesLabel}))
        if not self.destroyed:
            self.officesScroll.Load(contentList=scrolllist)

    def LoadButtons(self):
        if self.destroyed:
            return
        btns = []
        officeExists = self.controller.DoesOfficeExist()
        canRent = self.controller.CanRent()
        canUnrent = self.controller.CanUnrent()
        canMoveHQ = self.controller.CanMoveHQ()
        hqAllowed = self.controller.IsHqAllowed()
        if canRent and not officeExists:
            rentLabel = GetByLabel('UI/Station/Lobby/RentOffice')
            btns.append([rentLabel, self.RentOffice, None])
        if canUnrent and officeExists:
            btns.append([GetByLabel('UI/Station/Hangar/UnrentOffice'), self.UnrentOffice, None])
        if canMoveHQ and hqAllowed:
            isHQHere = self.controller.IsMyHQ()
            if not isHQHere:
                hqLabel = GetByLabel('UI/Station/Lobby/MoveHeadquartersHere')
                btns.append([hqLabel, self.SetHQ, None])
            if not officeExists and self.controller.HasCorpImpountedItems():
                btns.append([GetByLabel('UI/Inventory/ReleaseItems'), self.ReleaseImpoundedItems, None])
        if self.controller.MyCorpIsOwner():
            mgmtLabel = GetByLabel('UI/Station/Lobby/StationManagement')
            btns.append([mgmtLabel, self.OpenStationManagement, None])
        if self.destroyed:
            return
        self.officesButtons.Flush()
        for label, func, args in btns:
            Button(parent=self.officesButtons, label=label, func=func, args=args, align=uiconst.NOALIGN)

    def RentOffice(self, *args):
        if self.sr.isRentOfficeOpening:
            return
        self.sr.isRentOfficeOpening = 1
        try:
            cost = self.controller.GetCostForOpeningOffice()
            if eve.Message('AskPayOfficeRentalFee', {'cost': cost,
             'duration': const.rentalPeriodOffice * const.DAY}, uiconst.YESNO) == uiconst.ID_YES:
                officeID = self.controller.RentOffice(cost)
                if officeID:
                    self.InvalidateOfficeInvCache(officeID)
            uthread.new(self.LoadButtons)
            if self.selectedGroupButtonID == OFFICESPANEL:
                self.ShowOffices()
        finally:
            self.sr.isRentOfficeOpening = 0

    def InvalidateOfficeInvCache(self, officeID):
        office = self.controller.GetMyCorpOffice()
        invCache = sm.GetService('invCache')
        invCache.InvalidateLocationCache(officeID)
        if office is not None:
            itemID = self.controller.GetItemID()
            folder = invCache.GetInventoryFromId(office.officeFolderID, locationID=itemID)
            folder.List()
            wnd = InventoryWindow.GetIfOpen()
            if not wnd:
                InventoryWindow.OpenOrShow()

    def UnrentOffice(self, *args):
        corpHasItemsInStation = self.controller.CorpHasItemsInstaton()
        if corpHasItemsInStation:
            if eve.Message('crpUnrentOfficeWithContent', {}, uiconst.YESNO) != uiconst.ID_YES:
                return
        elif eve.Message('crpUnrentOffice', {}, uiconst.YESNO) != uiconst.ID_YES:
            return
        self.controller.UnrentOffice()

    def SetHQ(self, *args):
        self.controller.SetHQ()

    def ReleaseImpoundedItems(self, *args):
        cost = self.controller.GetCostForGettingCorpJunkBack()
        if eve.Message('CrpJunkAcceptCost', {'cost': FmtAmt(cost)}, uiconst.YESNO) != uiconst.ID_YES:
            return
        self.controller.ReleaseImpoundedItems(cost)
        self.LoadButtons()

    def OpenStationManagement(self, *args):
        uthread.new(self.controller.OpenStationMgmt)

    def ReloadOfficesIfVisible(self):
        if self.selectedGroupButtonID == OFFICESPANEL:
            self.ShowOffices()

    def _FindAvailableAndUnavailableAgents(self, agentsInStation, localRelevantAgents, relevantAgents):
        epicArcStatusSvc = sm.RemoteSvc('epicArcStatus')
        facWarSvc = sm.StartService('facwar')
        standingSvc = sm.StartService('standing')
        unavailableAgents = []
        availableAgents = []
        for agent in agentsInStation:
            if agent.agentID in const.rookieAgentList:
                continue
            isLimitedToFacWar = False
            if agent.agentTypeID == const.agentTypeFactionalWarfareAgent and facWarSvc.GetCorporationWarFactionID(agent.corporationID) != session.warfactionid:
                isLimitedToFacWar = True
            normalAgants = (const.agentTypeResearchAgent,
             const.agentTypeBasicAgent,
             const.agentTypeEventMissionAgent,
             const.agentTypeCareerAgent,
             const.agentTypeFactionalWarfareAgent)
            if agent.agentTypeID in normalAgants:
                standingIsValid = self._CheckCanUseAgent(agent, standingSvc)
                haveMissionFromAgent = agent.agentID in relevantAgents
                if not isLimitedToFacWar and (standingIsValid or haveMissionFromAgent):
                    availableAgents.append(agent.agentID)
                else:
                    unavailableAgents.append(agent.agentID)
            elif agent.agentTypeID == const.agentTypeEpicArcAgent:
                standingIsValid = self._CheckCanUseAgent(agent, standingSvc)
                haveMissionFromAgent = agent.agentID in relevantAgents
                epicAgentAvailable = False
                if haveMissionFromAgent:
                    epicAgentAvailable = True
                elif standingIsValid:
                    if agent.agentID in relevantAgents or epicArcStatusSvc.AgentHasEpicMissionsForCharacter(agent.agentID):
                        epicAgentAvailable = True
                if epicAgentAvailable:
                    availableAgents.append(agent.agentID)
                else:
                    unavailableAgents.append(agent.agentID)
            if agent.agentTypeID == const.agentTypeAura:
                if sm.GetService('experimentClientSvc').IsTutorialEnabled():
                    availableAgents.append(agent.agentID)
            elif agent.agentTypeID in (const.agentTypeGenericStorylineMissionAgent, const.agentTypeStorylineMissionAgent):
                if agent.agentID in localRelevantAgents:
                    availableAgents.append(agent.agentID)
                else:
                    unavailableAgents.append(agent.agentID)

        return (availableAgents, unavailableAgents)

    def _CheckCanUseAgent(self, agent, standingSvc):
        return standingSvc.CanUseAgent(agent.factionID, agent.corporationID, agent.agentID, agent.level, agent.agentTypeID)

    def ShowAgents(self):
        if self.selectedGroupButtonID != AGENTSPANEL:
            return
        try:
            agentsSvc = sm.GetService('agents')
            journalSvc = sm.GetService('journal')
            agentMissions = journalSvc.GetMyAgentJournalDetails()[:1][0]
            agentsInStation = self.controller.GetAgents()
            relevantAgents = []
            missionStateDict = {}
            for each in agentMissions:
                missionState, importantMission, missionType, missionName, agentID, expirationTime, bookmarks, remoteOfferable, remoteCompletable, contentID = each
                agent = agentsSvc.GetAgentByID(agentID)
                missionStateDict[agentID] = missionState
                onGoingMission = (const.agentMissionStateAllocated, const.agentMissionStateOffered)
                specialAgents = (const.agentTypeGenericStorylineMissionAgent,
                 const.agentTypeStorylineMissionAgent,
                 const.agentTypeEventMissionAgent,
                 const.agentTypeCareerAgent,
                 const.agentTypeEpicArcAgent)
                if missionState not in onGoingMission or agent.agentTypeID in specialAgents:
                    relevantAgents.append(agentID)

            localRelevantAgents = []
            for agent in agentsInStation:
                if agent.agentID in relevantAgents:
                    localRelevantAgents.append(agent.agentID)

            if self.destroyed:
                return
            scrolllist = []
            sortlist = []
            for agentID in relevantAgents:
                if not eve.rookieState or agentID in const.rookieAgentList:
                    if agentID not in localRelevantAgents:
                        entryWithSortValue = self.GetAgentEntryWithSortValue(agentID, missionStateDict)
                        sortlist.append(entryWithSortValue)

            if sortlist:
                agentLabel = GetByLabel('UI/Station/Lobby/AgentsOfInterest')
                scrolllist.append(GetListEntry('Header', {'label': agentLabel}))
                scrolllist += SortListOfTuples(sortlist)
            agentList, unavailableAgents = self._FindAvailableAndUnavailableAgents(agentsInStation, localRelevantAgents, relevantAgents)
            agentInfo = [('UI/Station/Lobby/AvailableToYou', agentList), ('UI/Station/Lobby/NotAvailableToYou', unavailableAgents)]
            for labelPath, agentList in agentInfo:
                if agentList:
                    text = GetByLabel(labelPath)
                    scrolllist.append(GetListEntry('Header', {'label': text}))
                    sortlist = []
                    for agentID in agentList:
                        entryWithSortValue = self.GetAgentEntryWithSortValue(agentID, missionStateDict)
                        sortlist.append(entryWithSortValue)

                    scrolllist += SortListOfTuples(sortlist)

            if self.destroyed:
                return
            self.agentScroll.Load(fixedEntryHeight=40, contentList=scrolllist)
        except:
            log.LogException()
            sys.exc_clear()

    def GetAgentEntryWithSortValue(self, agentID, missionStateDict):
        missionState = missionStateDict.get(agentID)
        sortValue = cfg.eveowners.Get(agentID).name
        entry = GetListEntry('AgentEntry', {'charID': agentID,
         'missionState': missionState})
        return (sortValue, entry)

    def ShowGuests(self, *args):
        if self.selectedGroupButtonID != GUESTSPANEL:
            return
        guests = self.controller.GetGuests()
        ownerIDs = guests.keys()
        cfg.eveowners.Prime(ownerIDs)
        guestFilter = self.quickFilter.GetValue()
        if len(guestFilter):
            filterData = [ KeyVal(name=cfg.eveowners.Get(charID).name, charID=charID) for charID in ownerIDs ]
            filterGuests = NiceFilter(self.quickFilter.QuickFilter, filterData)
            ownerIDs = [ each.charID for each in filterGuests ]
        if self.destroyed:
            return
        scrolllist = []
        for charID in ownerIDs:
            if charID not in guests:
                continue
            corpID, allianceID, warFactionID = guests[charID]
            charinfo = cfg.eveowners.Get(charID)
            sortValue = charinfo.name.lower()
            data = {'charID': charID,
             'info': charinfo,
             'label': charinfo.name,
             'corpID': corpID,
             'allianceID': allianceID,
             'warFactionID': warFactionID}
            entry = GetListEntry(self.userEntry, data)
            scrolllist.append((sortValue, entry))

        scrolllist = SortListOfTuples(scrolllist)
        self.guestScroll.Clear()
        self.guestScroll.AddNodes(0, scrolllist)
        self.UpdateGuestTabText()

    def OnCharNowInStation(self, rec):
        self.CharacterAdded(*rec)

    def OnCharNoLongerInStation(self, rec):
        self.CharacterRemoved(rec[0])

    def OnCharacterEnteredStructure(self, characterID, corporationID, allianceID, factionID):
        self.CharacterAdded(characterID, corporationID, allianceID, factionID)

    def OnCharacterLeftStructure(self, characterID):
        self.CharacterRemoved(characterID)

    @telemetry.ZONE_METHOD
    def CharacterAdded(self, characterID, corporationID, allianceID, factionID):
        if not self.IsLobbyBeAvailable():
            return
        self.UpdateGuestTabText()
        if self.selectedGroupButtonID != GUESTSPANEL:
            return
        cfg.eveowners.Prime([characterID])
        if self.destroyed:
            return
        newcharinfo = cfg.eveowners.Get(characterID)
        idx = 0
        for each in self.guestScroll.GetNodes():
            if each.charID == characterID:
                return
            if CaseFoldCompare(each.info.name, newcharinfo.name) > 0:
                break
            idx += 1

        filteredGuest = None
        guestFilter = self.quickFilter.GetValue()
        if len(guestFilter):
            filteredGuest = NiceFilter(self.quickFilter.QuickFilter, newcharinfo.name)
        if filteredGuest or len(guestFilter) == 0:
            data = {'charID': characterID,
             'info': newcharinfo,
             'label': newcharinfo.name,
             'corpID': corporationID,
             'allianceID': allianceID,
             'warFactionID': factionID}
            entry = GetListEntry(self.userEntry, data)
            self.guestScroll.AddNodes(idx, [entry])

    @telemetry.ZONE_METHOD
    def CharacterRemoved(self, characterID):
        if not self.IsLobbyBeAvailable():
            return
        self.UpdateGuestTabText()
        if self.selectedGroupButtonID != GUESTSPANEL:
            return
        for entry in self.guestScroll.GetNodes():
            if entry.charID == characterID:
                self.guestScroll.RemoveNodes([entry])
                return

    def IsLobbyBeAvailable(self):
        if self.destroyed:
            return False
        if not (session.stationid2 or IsDockedInStructure()):
            return False
        return True

    def OnProcessStationServiceItemChange(self, stationID, solarSystemID, maskServiceID, stationServiceItemID, isEnabled):
        if not self.IsLobbyBeAvailable():
            return
        for icon in self.serviceButtons.children:
            if hasattr(icon, 'maskStationServiceIDs') and maskServiceID in icon.maskStationServiceIDs:
                serviceID = stationServiceConst.serviceIdByMaskId[maskServiceID]
                self.SetServiceButtonState(icon, serviceID)

    def OnStructureServiceUpdated(self):
        self.ReloadServiceButtons()

    def OnAgentMissionChange(self, actionID, agentID, tutorialID = None):
        if self.selectedGroupButtonID == AGENTSPANEL:
            self.ShowAgents()

    def OnStandingSet(self, fromID, toID, rank):
        if self.selectedGroupButtonID == AGENTSPANEL:
            self.ShowAgents()

    def OnCorporationChanged(self, corpID, change):
        blue.pyos.synchro.Sleep(750)
        self.LoadButtons()

    def OnCorporationMemberChanged(self, corporationID, memberID, change):
        if memberID == session.charid:
            self.LoadButtons()

    def OnPrimaryViewChanged(self, oldViewInfo, newViewInfo):
        self.UpdateDockedModeBtn(newViewInfo.name)

    def StopAllBlinkButtons(self):
        for each in self.serviceButtons.children:
            if hasattr(each, 'Blink'):
                each.Blink(0)

    def BlinkButton(self, whatBtn):
        for each in self.serviceButtons.children:
            if each.name.lower() == whatBtn.lower():
                each.Blink(blinks=40)
