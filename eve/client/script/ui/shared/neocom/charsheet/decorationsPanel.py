#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\charsheet\decorationsPanel.py
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control import entries
from eve.client.script.ui.control.buttonGroup import ButtonGroup
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.tabGroup import TabGroup
import carbonui.const as uiconst
from eve.client.script.ui.shared.neocom.charsheet.charSheetUtil import GetMedalScrollEntries
from eve.client.script.ui.util.uix import ListWnd
from localization import GetByLabel
PANEL_PERMISSIONS = 'mydecorations_permissions'
PANEL_MEDALS = 'mydecorations_medals'
PANEL_RANKS = 'mydecorations_ranks'

class DecorationsPanel(Container):
    default_name = 'DecorationsPanel'
    __notifyevents__ = ['OnRankChange', 'OnUpdatedMedalsAvailable', 'OnUpdatedMedalStatusAvailable']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        btns = [(GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/SaveDecorationPermissionChanges'),
          self.SaveDecorationPermissionsChanges,
          (),
          64), (GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/SetAllDecorationPermissions'),
          self.SetAllDecorationPermissions,
          (),
          64)]
        self.mainAreaButtons = ContainerAutoSize(align=uiconst.TOBOTTOM, parent=self)
        ButtonGroup(btns=btns, parent=self.mainAreaButtons, line=False)
        self.decoMedalList = None
        self.decoRankList = None
        self.scroll = Scroll(parent=self, padding=(0, 4, 0, 4))
        self.mydecorationstabs = TabGroup(name='tabparent', parent=self, idx=0, tabs=[[GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Ranks'),
          self.scroll,
          self,
          PANEL_RANKS], [GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Medals'),
          self.scroll,
          self,
          PANEL_MEDALS], [GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Permissions'),
          self.scroll,
          self,
          PANEL_PERMISSIONS]], groupID='cs_decorations')

    def LoadPanel(self, *args):
        self.mydecorationstabs.AutoSelect()

    def SaveDecorationPermissionsChanges(self):
        promptForDelete = False
        changes = {}
        for entry in self.scroll.GetNodes():
            if entry.panel and hasattr(entry.panel, 'flag'):
                if entry.panel.HasChanged():
                    if entry.panel.flag == 1:
                        promptForDelete = True
                    changes[entry.panel.sr.node.itemID] = entry.panel.flag

        if promptForDelete == False or uicore.Message('DeleteMedalConfirmation', {}, uiconst.YESNO) == uiconst.ID_YES:
            if len(changes) > 0:
                sm.StartService('medals').SetMedalStatus(changes)
        self.decoMedalList = None

    def SetAllDecorationPermissions(self):
        permissionList = [(GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Private'), 2), (GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Public'), 3)]
        pickedPermission = ListWnd(permissionList, 'generic', GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/SetAllDecorationPermissions'), GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/SaveAllChangesImmediately'), windowName='permissionPickerWnd')
        if not pickedPermission:
            return
        permissionID = pickedPermission[1]
        m, _ = sm.StartService('medals').GetMedalsReceived(session.charid)
        myDecos = []
        for each in m:
            if each.status != 1:
                myDecos.append(each.medalID)

        myDecos = list(set(myDecos))
        updateDict = {}
        for decoID in myDecos:
            updateDict[decoID] = permissionID

        if len(updateDict) > 0:
            sm.StartService('medals').SetMedalStatus(updateDict)
            self.decoMedalList = None
            self.ShowMyDecorations('mydecorations_permissions')

    def Load(self, key):
        self.ShowMyDecorations(key)

    def ShowMyDecorations(self, key = None):
        if key == PANEL_RANKS:
            self.ShowMyRanks()
        elif key == PANEL_MEDALS:
            self.ShowMyMedals()
        elif key == PANEL_PERMISSIONS:
            self.ShowMyDecorationPermissions()

    def ShowMyMedals(self, charID = None):
        self.mainAreaButtons.Hide()
        if charID is None:
            charID = session.charid
        if self.decoMedalList is None:
            self.decoMedalList = GetMedalScrollEntries(charID)
        self.scroll.sr.id = 'charsheet_mymedals'
        self.scroll.Load(contentList=self.decoMedalList, noContentHint=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/NoMedals'))

    def ShowMyRanks(self):
        self.mainAreaButtons.Hide()
        if self.decoRankList is None:
            scrolllist = []
            characterRanks = sm.StartService('facwar').GetCharacterRankOverview(session.charid)
            for characterRank in characterRanks:
                entry = sm.StartService('info').GetRankEntry(characterRank)
                if entry:
                    scrolllist.append(entry)

            self.decoRankList = scrolllist[:]
        self.scroll.sr.id = 'charsheet_myranks'
        self.scroll.Load(contentList=self.decoRankList, noContentHint=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/NoRanks'))

    def ShowMyDecorationPermissions(self):
        self.mainAreaButtons.Show()
        scrollHeaders = [GetByLabel('UI/CharacterCreation/FirstName'),
         GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Private'),
         GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Public'),
         GetByLabel('UI/PI/Common/Remove')]
        self.scroll.sr.fixedColumns = {GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Private'): 60,
         GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Public'): 60}
        self.scroll.sr.id = 'charsheet_decopermissions'
        self.scroll.Load(contentList=[], headers=scrollHeaders)
        self.scroll.OnColumnChanged = self.OnDecorationPermissionsColumnChanged
        publicDeco = sm.StartService('medals').GetMedalsReceivedWithFlag(session.charid, [3])
        privateDeco = sm.StartService('medals').GetMedalsReceivedWithFlag(session.charid, [2])
        ppKeys = [ each for each in publicDeco.keys() + privateDeco.keys() ]
        scrolllist = []
        inMedalList = []
        characterMedals, characterMedalInfo = sm.StartService('medals').GetMedalsReceived(session.charid)
        for characterMedal in characterMedals:
            medalID = characterMedal.medalID
            if medalID not in ppKeys:
                continue
            if medalID in inMedalList:
                continue
            inMedalList.append(medalID)
            details = characterMedalInfo.Filter('medalID')
            if details and details.has_key(medalID):
                details = details.get(medalID)
            entry = self.CreateDecorationPermissionsEntry(characterMedal)
            if entry:
                scrolllist.append(entry)

        self.scroll.Load(contentList=scrolllist, headers=scrollHeaders, noContentHint=GetByLabel('UI/Common/NothingFound'))
        self.OnDecorationPermissionsColumnChanged()

    def CreateDecorationPermissionsEntry(self, data):
        entry = {'line': 1,
         'label': data.title + '<t><t><t>',
         'itemID': data.medalID,
         'visibilityFlags': data.status,
         'indent': 3,
         'selectable': 0}
        return entries.Get('DecorationPermissions', entry)

    def OnDecorationPermissionsColumnChanged(self, *args, **kwargs):
        for entry in self.scroll.GetNodes():
            if entry.panel and getattr(entry.panel, 'OnColumnChanged', None):
                entry.panel.OnColumnChanged()

    def OnRankChange(self, oldrank, newrank):
        if not session.warfactionid:
            return
        self.decoRankList = None
        if self.display:
            self.LoadPanel()

    def OnUpdatedMedalsAvailable(self):
        self.ReloadMedals()

    def OnUpdatedMedalStatusAvailable(self):
        self.ReloadMedals()

    def ReloadMedals(self):
        self.decoMedalList = None
        if self.display:
            self.LoadPanel()
