#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\dockedUI\inControlCont.py
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.buttonGroup import ButtonGroup
from eve.client.script.ui.control.eveIcon import GetLogoIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelSmall
from eve.client.script.ui.control.eveWindow import Window
import localization
import uthread

class PlayerInControlCont(ContainerAutoSize):
    default_alignMode = uiconst.TOPLEFT
    maxTextWidth = 300

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        charID = attributes.charID
        parentLayoutGrid = LayoutGrid(parent=self, columns=2, align=uiconst.TOPLEFT, padding=6, cellSpacing=(10, 10))
        addHeader = attributes.get('addHeader', True)
        if addHeader:
            self.AddHeader(parentLayoutGrid)
        sprite = Sprite(parent=parentLayoutGrid, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, pos=(0, 0, 128, 128))
        sm.GetService('photo').GetPortrait(charID, 128, sprite, allowServerTrip=True)
        subLayoutGrid = LayoutGrid(parent=parentLayoutGrid, columns=2, align=uiconst.TOPLEFT)
        spacer = Fill(align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, width=128, height=1, color=(0, 0, 0, 0))
        subLayoutGrid.AddCell(cellObject=spacer, colSpan=2)
        parallelCalls = []
        parallelCalls.append((sm.RemoteSvc('charMgr').GetPublicInfo3, (charID,)))
        parallelCalls.append((sm.GetService('corp').GetInfoWindowDataForChar, (charID, 1)))
        charinfo, corpCharInfo = uthread.parallel(parallelCalls)
        charName = cfg.eveowners.Get(charID).name
        nameLabel = EveLabelMedium(text=charName, autoFitToText=True)
        subLayoutGrid.AddCell(cellObject=nameLabel, colSpan=2)
        titleText = self.GetTitleText(corpCharInfo)
        titleLabel = EveLabelMedium(text=titleText, autoFitToText=True)
        if titleLabel.textwidth > self.maxTextWidth:
            titleLabel.width = self.maxTextWidth
        subLayoutGrid.AddCell(cellObject=titleLabel, colSpan=2)
        if corpCharInfo:
            corpID = corpCharInfo.corpID
            allianceID = corpCharInfo.allianceID
            for eachID in (corpID, allianceID):
                if eachID:
                    logo = self.GetLogo(eachID)
                    logo.hint = cfg.eveowners.Get(eachID).name
                    subLayoutGrid.AddCell(cellObject=logo)

    def AddHeader(self, parent):
        self.headerLabel = EveLabelSmall(text=localization.GetByLabel('UI/Station/PilotInControl'), padbottom=6)
        parent.AddCell(cellObject=self.headerLabel, colSpan=2)

    def GetTitleText(self, corpCharInfo):
        titleList = []
        if corpCharInfo.title:
            titleList.append(corpCharInfo.title)
        for i in xrange(1, 17):
            titleText = getattr(corpCharInfo, 'title%s' % i, None)
            if titleText:
                titleList.append(titleText)

        if len(titleList):
            title = localization.formatters.FormatGenericList(titleList)
            return title
        else:
            return

    def GetLogo(self, corpID):
        logo = GetLogoIcon(itemID=corpID, state=uiconst.UI_NORMAL, align=uiconst.TOPLEFT, pos=(0, 0, 64, 64), ignoreSize=True)
        return logo


class ConfirmTakeControl(Window):
    __guid__ = 'ConfirmTakeControl'
    default_captionLabelPath = 'UI/Station/PilotInControl'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.MakeUnResizeable()
        self.controller = attributes.controller
        charInControl = attributes.charInControl
        self.SetTopparentHeight(0)
        self.btnGroup = ButtonGroup(parent=self.sr.main, idx=0)
        self.btnGroup.AddButton(localization.GetByLabel('UI/Commands/TakeStructureControl'), self.TakeControl)
        self.btnGroup.AddButton(localization.GetByLabel('UI/Generic/Cancel'), self.Cancel)
        self.playerCont = PlayerInControlCont(parent=self.sr.main, align=uiconst.CENTERTOP, addHeader=False, charID=charInControl, callback=self.OnContainerResized)
        self.SetCaption(localization.GetByLabel('UI/Station/PilotInControl'))
        self.ShowModal()

    def OnContainerResized(self):
        w, h = self.playerCont.GetAutoSize()
        self.height = self.btnGroup.height + h + self.sr.headerParent.height
        self.width = max(w, 300)

    def TakeControl(self, *args):
        try:
            self.controller.TakeControl()
        finally:
            self.Close()

    def Cancel(self, *args):
        self.CloseByUser()
