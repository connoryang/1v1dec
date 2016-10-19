#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\searchCont.py
from carbonui.primitives.container import Container
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.quickFilter import QuickFilterEdit
from localization import GetByLabel
import carbonui.const as uiconst
FITTING_MODE = 0
HARDWARE_MODE = 1

class SearchCont(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.searchFunc = attributes.searchFunc
        self.searchMode = None
        self.configValue = ''
        rightPadding = 0
        self.searchInput = QuickFilterEdit(name='searchField', parent=self, setvalue='', hinttext=GetByLabel('UI/Market/Marketbase/SearchTerm'), pos=(0, 0, 18, 0), padRight=rightPadding, maxLength=64, align=uiconst.TOTOP, OnClearFilter=self.Search)
        self.searchInput.OnReturn = self.Search
        self.searchInput.ReloadFunction = self.Search

    def ChangeSearchMode(self, searchMode):
        self.searchMode = searchMode
        if searchMode == HARDWARE_MODE:
            self.configValue = 'fitting_hardwareSearchField'
        else:
            self.configValue = 'fitting_fittingSearchField'
        searchString = settings.user.ui.Get(self.configValue, '')
        self.searchInput.SetValue(searchString)

    def Search(self):
        searchString = self.searchInput.GetValue()
        settingConfig = self.configValue
        self.searchFunc(settingConfig, searchString)
