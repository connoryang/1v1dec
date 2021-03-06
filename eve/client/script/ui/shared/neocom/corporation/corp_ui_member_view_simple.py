#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\corporation\corp_ui_member_view_simple.py
import uiprimitives
import uicontrols
import uthread
import uix
import listentry
import carbonui.const as uiconst
import localization
import util

class CorpMembersViewSimple(uiprimitives.Container):
    __guid__ = 'form.CorpMembersViewSimple'
    __nonpersistvars__ = []

    def ApplyAttributes(self, attributes):
        uiprimitives.Container.ApplyAttributes(self, attributes)
        self.memberIDs = []
        self.viewPerPage = 10
        self.viewFrom = 0
        self.labelResults = None

    def CreateWindow(self):
        wndOutputArea = uiprimitives.Container(name='output', parent=self, align=uiconst.TOTOP, height=48)
        captionparent = uiprimitives.Container(name='captionparent', parent=wndOutputArea, align=uiconst.TOTOP, width=136, height=16)
        self.labelResults = uicontrols.EveLabelMedium(text=localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/SimpleView/ResultsLabel'), parent=captionparent, align=uiconst.TOTOP, height=16, state=uiconst.UI_NORMAL)
        wndResultsBar = uiprimitives.Container(name='results', parent=wndOutputArea, align=uiconst.TOTOP, height=16)
        wndNavBtns = uiprimitives.Container(name='sidepar', parent=wndResultsBar, align=uiconst.TORIGHT, width=52)
        label = uiprimitives.Container(name='text', parent=wndResultsBar, align=uiconst.TOLEFT, width=150, height=16)
        uicontrols.EveLabelMedium(text=localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/SimpleView/MembersPerPage'), parent=label, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        optlist = [[util.FmtAmt(10), 10],
         [util.FmtAmt(25), 25],
         [util.FmtAmt(50), 50],
         [util.FmtAmt(100), 100],
         [util.FmtAmt(500), 500]]
        countcombo = uicontrols.Combo(label='', parent=wndResultsBar, options=optlist, name='membersperpage', callback=self.OnComboChange, width=146, pos=(150, 0, 0, 0))
        countcombo.sr.label.width = 200
        countcombo.sr.label.top = -16
        self.sr.MembersPerPage = countcombo
        btn = uix.GetBigButton(24, wndNavBtns, 0, 0)
        btn.OnClick = (self.Navigate, -1)
        btn.hint = localization.GetByLabel('UI/Common/Previous')
        btn.state = uiconst.UI_HIDDEN
        btn.sr.icon.LoadIcon('ui_23_64_1')
        self.backBtn = btn
        btn = uix.GetBigButton(24, wndNavBtns, 24, 0)
        btn.OnClick = (self.Navigate, 1)
        btn.hint = localization.GetByLabel('UI/Common/ViewMore')
        btn.state = uiconst.UI_HIDDEN
        btn.sr.icon.LoadIcon('ui_23_64_2')
        self.fwdBtn = btn
        uiprimitives.Container(name='push', parent=wndOutputArea, align=uiconst.TOTOP, height=24)
        self.outputScrollContainer = uiprimitives.Container(name='output', parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.scroll = uicontrols.Scroll(parent=self.outputScrollContainer)

    def PopulateView(self, memberIDs = None):
        if memberIDs is not None:
            self.memberIDs = memberIDs
            self.labelResults.text = (localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/SimpleView/ResultsLabelPopulated', numResults=len(self.memberIDs)),)
        else:
            self.labelResults.text = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/SimpleView/ResultsLabel')
        nFrom = self.viewFrom
        nTo = nFrom + self.viewPerPage
        scrolllist = []
        memberIDsToDisplay = []
        for memberID in self.memberIDs:
            memberIDsToDisplay.append(memberID)

        cfg.eveowners.Prime(memberIDsToDisplay)
        totalNum = len(memberIDsToDisplay)
        if totalNum is not None:
            self.ShowHideBrowse(totalNum)
        for charID in memberIDsToDisplay:
            scrolllist.append(listentry.Get('User', {'charID': charID}))

        scrolllist = scrolllist[nFrom:nTo]
        self.scroll.Load(None, scrolllist)

    def OnComboChange(self, entry, header, value, *args):
        if entry.name == 'membersperpage':
            self.viewPerPage = value
            uthread.new(self.PopulateView)

    def Navigate(self, direction, *args):
        self.viewFrom = max(0, self.viewFrom + direction * self.viewPerPage)
        uthread.new(self.PopulateView)

    def ShowHideBrowse(self, totalNum):
        if self.viewFrom == 0:
            self.backBtn.state = uiconst.UI_HIDDEN
        else:
            self.backBtn.state = uiconst.UI_NORMAL
        if self.viewFrom + self.viewPerPage >= totalNum:
            self.fwdBtn.state = uiconst.UI_HIDDEN
        else:
            self.fwdBtn.state = uiconst.UI_NORMAL
