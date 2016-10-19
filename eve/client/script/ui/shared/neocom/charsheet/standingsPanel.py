#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\charsheet\standingsPanel.py
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.tabGroup import TabGroup
from localization import GetByLabel

class StandingsPanel(Container):
    default_name = 'StandingsPanel'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.scroll = Scroll(parent=self, padding=(0, 4, 0, 4))
        self.scroll.sr.id = 'charsheet_standings'
        self.tabs = TabGroup(name='tabparent', parent=self, idx=0, tabs=((GetByLabel('UI/CharacterSheet/CharacterSheetWindow/StandingTabs/LikedBy'),
          self.scroll,
          self,
          'mystandings_to_positive'), (GetByLabel('UI/CharacterSheet/CharacterSheetWindow/StandingTabs/DislikeBy'),
          self.scroll,
          self,
          'mystandings_to_negative')), groupID='cs_standings')

    def LoadPanel(self, *args):
        self.tabs.AutoSelect()

    def Load(self, key):
        positive = key == 'mystandings_to_positive'
        scrolllist = sm.GetService('standing').GetStandingEntries(positive, session.charid)
        self.scroll.Load(contentList=scrolllist)
