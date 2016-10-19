#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\missingItemsPopup.py
import evetypes
from carbon.common.script.sys.serviceConst import ROLE_GMH
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.ui.control.buttonGroup import ButtonGroup
from eve.client.script.ui.control.eveLabel import EveCaptionLarge, EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.eveWindow import Window
import carbonui.const as uiconst
from eve.common.lib.appConst import defaultPadding
from localization import GetByLabel
from shipfitting.multiBuyUtil import BuyMultipleTypesWithQty
from utillib import KeyVal
from eve.client.script.ui.control import entries as listentry

class BuyAllMessageBox(Window):
    __guid__ = 'BuyAllMessageBox'
    default_width = 340
    default_height = 210

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.sr.main.clipChildren = True
        self.MakeUnMinimizable()
        self.HideHeader()
        descText = attributes.missingText
        self.faildToLoadInfo = attributes.faildToLoadInfo
        title = GetByLabel('UI/Common/Information')
        caption = EveCaptionLarge(text=title, align=uiconst.CENTERLEFT, parent=self.sr.topParent, left=64, width=270)
        self.SetTopparentHeight(max(56, caption.textheight + 16))
        self.SetWndIcon('res:/ui/Texture/WindowIcons/info.png')
        descLabel = EveLabelMedium(parent=self.sr.main, text=descText, align=uiconst.TOTOP, padding=(11,
         11,
         defaultPadding,
         defaultPadding))
        buttonGroup = ButtonGroup(parent=self.sr.main, unisize=1, idx=0)
        buyAllBtn = buttonGroup.AddButton(GetByLabel('UI/Market/MarketQuote/BuyAll'), self.BuyAll)
        closeBtn = buttonGroup.AddButton(GetByLabel('/Carbon/UI/Common/Close'), self.Close)
        if session.role & ROLE_GMH == ROLE_GMH:
            buttonGroup.AddButton('GM: Give all', self.GiveAllGM)
        self.typeScroll = Scroll(name='typeScroll', parent=self.sr.main, padding=(defaultPadding,
         0,
         defaultPadding,
         0))
        self.LoadTypes(self.faildToLoadInfo)

    def LoadTypes(self, typeIDsAndQty):
        scrolllist = []
        for eachTypeID, qty in typeIDsAndQty.iteritems():
            typeName = evetypes.GetName(eachTypeID)
            label = '%sx %s' % (qty, typeName)
            data = KeyVal(label=label, typeID=eachTypeID, itemID=None, getIcon=1)
            scrolllist.append((typeName, listentry.Get('Item', data=data)))

        scrolllist = SortListOfTuples(scrolllist)
        self.typeScroll.Load(contentList=scrolllist)
        self.height = self.GetNewHeight()

    def BuyAll(self, *args):
        BuyMultipleTypesWithQty(self.faildToLoadInfo)
        self.Close()

    def GetNewHeight(self):
        contentHeight = self.typeScroll.GetContentHeight()
        newHeight = 150 + contentHeight
        return min(400, newHeight)

    def GiveAllGM(self, *args):
        missingDict = self.faildToLoadInfo
        numToCountTo = len(missingDict) + 1
        header = 'GM Item Gift'
        sm.GetService('loading').ProgressWnd(header, '', 1, numToCountTo)
        counter = 1
        for typeID, qty in missingDict.iteritems():
            counter += 1
            sm.GetService('loading').ProgressWnd(header, '', counter, numToCountTo)
            sm.RemoteSvc('slash').SlashCmd('/create %s %s' % (typeID, qty))

        sm.GetService('loading').ProgressWnd('Done', '', numToCountTo, numToCountTo)
        self.Close()
