#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\assets\assetSafety.py
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.util.bunch import Bunch
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.shared.assets.assetSafetyEntry import AssetSafetyEntry
import blue
from localization import GetByLabel

class AssetSafetyCont(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.assetSafetyController = attributes.controller
        self.assetSafetyScroll = Scroll(name='assetSafetyScroll', id='assetSafetyScrollGUID', parent=self, align=uiconst.TOALL)
        self.updateCounter = None

    def Load(self):
        scrollList = GetAssetSafetyScrollContent(self.assetSafetyController)
        headers = AssetSafetyEntry.GetHeaders()
        self.assetSafetyScroll.sr.minColumnWidth = AssetSafetyEntry.GetMinimumColWidth()
        self.assetSafetyScroll.sr.defaultColumnWidth = AssetSafetyEntry.GetDefaultColumnWidth()
        self.assetSafetyScroll.Load(contentList=scrollList, headers=headers, noContentHint=GetByLabel('UI/Corporations/Assets/NoItemsFound'))
        self.updateCounter = AutoTimer(1000, self.UpdateCounters_thread)

    def UpdateCounters_thread(self):
        for eachEntry in self.assetSafetyScroll.GetNodes():
            panel = getattr(eachEntry, 'panel', None)
            if not panel or panel.destroyed:
                continue
            if isinstance(panel, AssetSafetyEntry):
                panel.UpdateProgress()

    def Close(self):
        Container.Close(self)
        self.updateCounter = None


def GetAssetSafetyScrollContent(controller):
    scrollList = []
    safetyRowSet = controller.GetItemsInSafety()
    for safetyData in safetyRowSet:
        node = Bunch(safetyData=safetyData, decoClass=AssetSafetyEntry, sortValues=AssetSafetyEntry.GetColumnSortValues(safetyData), label='<t>'.join(AssetSafetyEntry.GetNameAndSystem(safetyData)))
        scrollList.append(node)
        blue.pyos.BeNice()

    return scrollList
