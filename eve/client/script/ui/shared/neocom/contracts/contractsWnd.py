#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\contracts\contractsWnd.py
import sys
import form
import localization
import uicontrols
import uiprimitives
import uiutil
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.shared.neocom.contracts.contractPanels import StartPagePanel, MyContractsPanel

class ContractsWindow(uicontrols.Window):
    __guid__ = 'form.ContractsWindow'
    __notifyevents__ = ['OnDeleteContract', 'OnAddIgnore']
    default_width = 630
    default_height = 500
    default_windowID = 'contracts'
    default_captionLabelPath = 'Tooltips/Neocom/Contracts'
    default_descriptionLabelPath = 'Tooltips/Neocom/Contracts_description'
    default_iconNum = 'res:/ui/Texture/WindowIcons/contracts.png'

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        lookup = attributes.lookup
        idx = attributes.idx
        self.scope = 'all'
        self.SetWndIcon(self.iconNum, mainTop=-10)
        self.SetMinSize([700, 560])
        self.SetTopparentHeight(0)
        self.pages = {0: None}
        self.currPage = 0
        self.previousPageContractID = None
        self.currentPageContractID = None
        self.nextPageContractID = None
        self.parsingIssuers = False
        self.parsingType = False
        self.issuersByName = {}
        self.fetching = 0
        btns = ((localization.GetByLabel('UI/Inventory/ItemActions/CreateContract'),
          self.OpenCreateContract,
          None,
          None),)
        uicontrols.ButtonGroup(btns=btns, parent=self.sr.main, line=0, unisize=1)
        self.LoadTabs(lookup, idx)
        if lookup:
            self.LookupOwner(lookup)

    def OpenCreateContract(self, *args):
        sm.GetService('contracts').OpenCreateContract()

    def MouseEnterHighlightOn(self, wnd, *args):
        wnd.color.SetRGB(1.0, 1.0, 0.0)

    def MouseExitHighlightOff(self, wnd, *args):
        wnd.color.SetRGB(1.0, 1.0, 1.0)

    def LookupOwner(self, ownerName):
        try:
            self.Maximize()
            setattr(self.sr.myContractsParent, 'lookup', ownerName)
            self.sr.maintabs.SelectByIdx(1)
            self.sr.myContractsParent.sr.fltToFrom.SetValue(None)
            self.sr.myContractsParent.sr.fltOwner.SetValue(ownerName)
            self.sr.myContractsParent.sr.fltStatus.SelectItemByValue(const.conStatusFinished)
            self.sr.myContractsParent.sr.fltType.SelectItemByValue(None)
            self.sr.myContractsParent.FetchContracts()
        except:
            sys.exc_clear()

    def LoadTabs(self, lookup = None, idx = None):
        self.sr.startPageParent = StartPagePanel(name='startPageParent', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), state=uiconst.UI_HIDDEN, idx=1)
        self.sr.myContractsParent = MyContractsPanel(name='myContractsParent', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), state=uiconst.UI_HIDDEN, idx=1)
        self.sr.contractSearchParent = Container(name='contractSearchParent', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), state=uiconst.UI_HIDDEN, idx=1)
        self.sr.contractSearchContent = form.ContractSearchWindow(parent=self.sr.contractSearchParent, name='contractsearch', pos=(0, 0, 0, 0))
        self.sr.privateContractsParent = Container(name='privateContractsParent', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), state=uiconst.UI_HIDDEN, idx=1)
        tabs = uicontrols.TabGroup(name='contractsTabs', parent=self.sr.main, idx=0)
        tabList = [[localization.GetByLabel('UI/Contracts/ContractsWindow/StartPage'),
          self.sr.startPageParent,
          self,
          'startPage'], [localization.GetByLabel('UI/Contracts/ContractsWindow/MyContracts'),
          self.sr.myContractsParent,
          self,
          'myContracts'], [localization.GetByLabel('UI/Contracts/ContractsWindow/AvailableContracts'),
          self.sr.contractSearchParent,
          self,
          'contractSearch']]
        tabs.Startup(tabList, 'contractsTabs', autoselecttab=0)
        if idx:
            tabs.SelectByIdx(idx)
        elif lookup:
            setattr(self.sr.myContractsParent, 'lookup', lookup)
            tabs.SelectByIdx(1)
        else:
            h = getattr(sm.StartService('contracts'), 'hasContractWindowBeenOpened', False)
            if not h:
                tabs.SelectByIdx(0)
                setattr(sm.StartService('contracts'), 'hasContractWindowBeenOpened', True)
            else:
                tabs.AutoSelect()
        self.sr.maintabs = tabs

    def Load(self, key):
        doInit = self.TabNotInitiatedCheck(key)
        if key == 'myContracts':
            if doInit:
                self.sr.myContractsParent.Init()
        elif key == 'startPage':
            self.sr.startPageParent.Init()
        elif key == 'contractSearch':
            self.sr.contractSearchContent.Load(key)
            self.sr.contractSearchContent.SetInitialFocus()

    def TabNotInitiatedCheck(self, key):
        doInit = not getattr(self, 'init_%s' % key, False)
        setattr(self, 'init_%s' % key, True)
        return doInit

    def Confirm(self, *etc):
        if self.sr.maintabs.GetSelectedArgs() == 'availableContracts':
            self.OnReturn_AvailableContracts()

    def GetError(self, checkNumber = 1):
        return ''

    def Error(self, error):
        if error:
            eve.Message('CustomInfo', {'info': error})

    def OnDeleteContract(self, contractID, *args):

        def DeleteContractInList(list, contractID):
            nodes = list.GetNodes()
            for n in nodes:
                if n.contractID == contractID:
                    list.RemoveEntries([n])
                    return

        list = uiutil.FindChild(self.sr.main, 'mycontractlist')
        if list:
            DeleteContractInList(list, contractID)

    def OnAddIgnore(self, ignoreID, *args):
        if self.sr.Get('contractlist'):
            list = self.sr.contractlist
        else:
            cont = self.sr.myContractsParent
            list = None
            for child in cont.children:
                if hasattr(child, 'name') and child.name == 'mycontractlist':
                    list = child
                    break
