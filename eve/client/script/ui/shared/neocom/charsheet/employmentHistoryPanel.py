#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\charsheet\employmentHistoryPanel.py
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveScroll import Scroll

class EmploymentHistoryPanel(Container):
    default_name = 'EmploymentHistoryPanel'
    __notifyevents__ = []

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.employmentList = None
        self.scroll = Scroll(parent=self, padding=(0, 4, 0, 4))
        self.scroll.sr.id = 'charsheet_employmenthistory'

    def LoadPanel(self, *args):
        if self.employmentList is None:
            self.employmentList = sm.GetService('info').GetEmploymentHistorySubContent(session.charid)
        self.scroll.Load(contentList=self.employmentList)

    def OnSessionChanged(self, isRemote, session, change):
        if 'corpid' in change:
            self.employmentList = None
        if self.display:
            self.LoadPanel()
