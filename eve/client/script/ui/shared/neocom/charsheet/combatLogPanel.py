#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\charsheet\combatLogPanel.py
from carbonui.primitives.container import Container
from eve.client.script.ui.control.checkbox import Checkbox
from eve.client.script.ui.control.eveCombo import Combo
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.shared.neocom.charsheet.charSheetUtil import GetCombatEntries
from eve.client.script.ui.util.uix import GetBigButton
import carbonui.const as uiconst
from localization import GetByLabel

class CombatLogPanel(Container):
    default_name = 'KillsPanel'
    __notifyevents__ = []

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.killentries = 25
        self.topCont = Container(name='combatlogpanel', parent=self, align=uiconst.TOTOP, padTop=const.defaultPadding)
        combatValues = ((GetByLabel('UI/Corporations/Wars/Killmails/ShowKills'), 0), (GetByLabel('UI/Corporations/Wars/Killmails/ShowLosses'), 1))
        selectedCombatType = settings.user.ui.Get('CombatLogCombo', 0)
        self.combatCombo = Combo(parent=self.topCont, name='combo', select=selectedCombatType, align=uiconst.TOPLEFT, left=1, callback=self.OnCombatChange, options=combatValues, idx=0, adjustWidth=True)
        self.sr.combatSetting = Checkbox(parent=self.topCont, align=uiconst.TOPLEFT, pos=(0,
         self.combatCombo.height + const.defaultPadding,
         300,
         14), configName='charsheet_condensedcombatlog', text=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/CondensedCombatLog'), checked=settings.user.ui.Get('charsheet_condensedcombatlog', 0), callback=self.CheckBoxChange)
        self.killReportQuickFilter = QuickFilterEdit(parent=self.topCont, left=const.defaultPadding, align=uiconst.TOPRIGHT, width=150)
        self.killReportQuickFilter.ReloadFunction = self.ReloadKillReports
        self.topCont.height = self.combatCombo.height + self.sr.combatSetting.height + const.defaultPadding
        self.btnContainer = Container(name='pageBtnContainer', parent=self, align=uiconst.TOBOTTOM, idx=0, padBottom=4)
        btn = GetBigButton(size=22, where=self.btnContainer, left=4, top=0)
        btn.SetAlign(uiconst.CENTERRIGHT)
        btn.hint = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/ViewMore')
        btn.sr.icon.LoadIcon('ui_23_64_2')
        btn = GetBigButton(size=22, where=self.btnContainer, left=4, top=0)
        btn.SetAlign(uiconst.CENTERLEFT)
        btn.hint = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/ViewPrevious')
        btn.sr.icon.LoadIcon('ui_23_64_1')
        self.btnContainer.height = max([ c.height for c in self.btnContainer.children ])
        self.scroll = Scroll(parent=self, padding=(0, 4, 0, 4))

    def CheckBoxChange(self, checkbox):
        if checkbox.name == 'charsheet_condensedcombatlog':
            settings.user.ui.Set('charsheet_condensedcombatlog', checkbox.checked)
            self.ShowKills()

    def OnCombatChange(self, *args):
        selected = self.combatCombo.GetValue()
        settings.user.ui.Set('CombatLogCombo', selected)
        self.combatPageNum = 0
        if selected == 0:
            self.ShowCombatKills()
        else:
            self.ShowCombatLosses()

    def LoadPanel(self, *args):
        self.ShowKills()

    def ShowKillsEx(self, recent, func, combatType, pageNum):
        if combatType == 'kills':
            prevType = self.prevKillIDs
        else:
            prevType = self.prevLossIDs
        filterText = self.killReportQuickFilter.GetValue().lower()
        scrolllist, headers = GetCombatEntries(recent, filterText=filterText)
        for c in self.btnContainer.children:
            c.state = uiconst.UI_HIDDEN

        self.btnContainer.state = uiconst.UI_HIDDEN
        killIDs = [ k.killID for k in recent ]
        prevbtn = self.btnContainer.children[1]
        nextbtn = self.btnContainer.children[0]
        if pageNum > 0:
            self.btnContainer.state = uiconst.UI_NORMAL
            prevbtn.state = uiconst.UI_NORMAL
            if combatType == 'kills':
                pageIndex = min(pageNum, len(self.prevKillIDs) - 1)
                prevType = self.prevKillIDs[pageIndex - 1]
            else:
                pageIndex = min(pageNum, len(self.prevLossIDs) - 1)
                prevType = self.prevLossIDs[pageIndex - 1]
            prevbtn.OnClick = (func, prevType, -1)
        maxKillIDs = max(killIDs) + 1 if killIDs else 0
        if combatType == 'kills' and pageNum + 1 > len(self.prevKillIDs):
            self.prevKillIDs.append(maxKillIDs)
        elif pageNum + 1 > len(self.prevLossIDs):
            self.prevLossIDs.append(maxKillIDs)
        if len(recent) >= self.killentries:
            self.btnContainer.state = uiconst.UI_NORMAL
            nextbtn.state = uiconst.UI_NORMAL
            nextbtn.OnClick = (func, min(killIDs), 1)
        isCondensed = settings.user.ui.Get('charsheet_condensedcombatlog', 0)
        if isCondensed:
            self.scroll.sr.id = 'charsheet_kills'
        else:
            self.scroll.sr.id = 'charsheet_kills2'
        noContentHintText = ''
        if combatType == 'kills':
            noContentHintText = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/NoKillsFound')
        elif combatType == 'losses':
            noContentHintText = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/NoLossesFound')
        pos = self.scroll.GetScrollProportion()
        self.scroll.Load(contentList=scrolllist, headers=headers, scrollTo=pos, noContentHint=noContentHintText)

    def ShowCombatKills(self, startFrom = None, pageChange = 0, *args):
        recent = sm.GetService('info').GetKillsRecentKills(self.killentries, startFrom)
        self.combatPageNum = max(0, self.combatPageNum + pageChange)
        self.ShowKillsEx(recent, self.ShowCombatKills, 'kills', pageNum=self.combatPageNum)

    def ShowCombatLosses(self, startFrom = None, pageChange = 0, *args):
        recent = sm.GetService('info').GetKillsRecentLosses(self.killentries, startFrom)
        self.combatPageNum = max(0, self.combatPageNum + pageChange)
        self.ShowKillsEx(recent, self.ShowCombatLosses, 'losses', pageNum=self.combatPageNum)

    def ShowKills(self):
        self.prevKillIDs = []
        self.prevLossIDs = []
        self.combatPageNum = 0
        selectedCombatType = settings.user.ui.Get('CombatLogCombo', 0)
        if selectedCombatType == 0:
            self.ShowCombatKills()
        else:
            self.ShowCombatLosses()

    def ReloadKillReports(self):
        combatSetting = settings.user.ui.Get('CombatLogCombo', 0)
        offset = None
        if combatSetting == 0:
            if self.prevKillIDs and self.combatPageNum:
                offset = self.prevKillIDs[self.combatPageNum]
            self.ShowCombatKills(offset)
        else:
            if self.prevLossIDs and self.combatPageNum:
                offset = self.prevLossIDs[self.combatPageNum]
            self.ShowCombatLosses(offset)
