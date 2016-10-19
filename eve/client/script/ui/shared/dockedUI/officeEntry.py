#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\dockedUI\officeEntry.py
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from eve.client.script.ui.control.buttonGroup import ButtonGroup
from eve.client.script.ui.control.eveIcon import GetLogoIcon
from eve.client.script.ui.control.eveLabel import EveLabelSmall, EveLabelMedium
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.themeColored import LineThemeColored
from inventorycommon.util import IsNPC
from localization import GetByLabel
import uthread

class OfficeEntry(SE_BaseClassCore):
    __guid__ = 'listentry.OfficeEntry'

    def Startup(self, *args):
        self.Flush()
        self.mainCont = Container(parent=self, align=uiconst.TOTOP, height=30)
        leftCont = Container(parent=self.mainCont, align=uiconst.TOLEFT, width=50)
        self.icon = Container(parent=leftCont, align=uiconst.TOPLEFT, pos=(3, 3, 32, 32))
        self.corpNameCont = Container(parent=self.mainCont, align=uiconst.TOTOP, height=17)
        label = GetByLabel('UI/Station/Lobby/CorpName')
        self.corpNameLabel = EveLabelSmall(text=label, parent=self.corpNameCont, left=5, top=2, state=uiconst.UI_DISABLED)
        self.corpNameText = EveLabelMedium(text='', parent=self.corpNameCont, left=5, state=uiconst.UI_NORMAL)
        LineThemeColored(parent=self, align=uiconst.TOBOTTOM)
        self.buttonCnt = Container(parent=self, align=uiconst.TOTOP, height=25, state=uiconst.UI_PICKCHILDREN)
        self.buttonCnt.display = False
        self.infoicon = InfoIcon(left=32, top=3, parent=leftCont, idx=0)

    def Load(self, node):
        self.sr.node = node
        data = node
        self.infoicon.UpdateInfoLink(const.typeCorporation, data.corpID)
        mainHeight = 0
        corpName = data.Get('corpName', '')
        self.corpNameText.text = corpName
        self.corpNameText.top = self.corpNameLabel.textheight
        self.corpNameCont.height = self.corpNameText.top + self.corpNameText.textheight + 2
        if self.corpNameCont.display:
            mainHeight += self.corpNameCont.height
        self.mainCont.height = mainHeight + 10
        self.icon.Flush()

        def LogoThread():
            if not self.destroyed:
                GetLogoIcon(itemID=data.corpID, parent=self.icon, acceptNone=False, align=uiconst.TOALL)

        uthread.new(LogoThread)
        self.buttonCnt.Flush()
        if not IsNPC(node.corpID):
            buttonEntries = []
            if session.corpid != node.corpID:
                if sm.GetService('corp').GetActiveApplication(node.corpID) is not None:
                    applyLabel = GetByLabel('UI/Corporations/CorpApplications/ViewApplication')
                else:
                    applyLabel = GetByLabel('UI/Corporations/CorporationWindow/Alliances/Rankings/ApplyToJoin')
                buttonEntries.append((applyLabel,
                 sm.GetService('corp').ApplyForMembership,
                 (node.corpID,),
                 80))
            self.buttonCnt.display = True
            if len(buttonEntries) > 0:
                self.buttonsGroup = ButtonGroup(btns=buttonEntries, parent=self.buttonCnt, unisize=0, line=0)
                self.buttonsGroup.top -= 1
        else:
            self.buttonCnt.display = False

    def GetHeight(self, *args):
        node, width = args
        lw, lh = EveLabelSmall.MeasureTextSize(text=GetByLabel('UI/Station/Lobby/CorpName'))
        tw, th = EveLabelMedium.MeasureTextSize(text=node.corpName)
        multiplier = 1
        height = 2
        height += (lh + th + 15) * multiplier
        height += 5
        if not IsNPC(node.corpID) and session.corpid != node.corpID:
            height += 30
        node.height = height
        return node.height
