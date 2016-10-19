#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\sidePanelButtons.py
import math
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.primitives.transform import Transform
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.shared.neocom.corporation.corp_ui_member_roleentry import VerticalLabel
from eve.client.script.ui.util.uiComponents import Component, ButtonEffect
import carbonui.const as uiconst
TABWIDTH = 18

@Component(ButtonEffect(opacityIdle=0.0, opacityHover=1.0, opacityMouseDown=1.0, bgElementFunc=lambda parent, _: parent.hilite, audioOnEntry='wise:/msg_ListEntryEnter_play', audioOnClick='wise:/msg_ListEntryClick_play'))

class SidePanelButtonWithText(Container):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(SidePanelButtonWithText, self).ApplyAttributes(attributes)
        self.isLeftAlign = attributes.isLeftAlign
        self.tabText = attributes.tabText
        self.onClick = attributes.onClick
        self.args = attributes.args
        self.isSelected = attributes.isSelected
        textRotation, frameRotation = self.GetRotations()
        self.tabLabelCont = VerticalLabel(parent=self, text=self.tabText, align=uiconst.CENTER, state=uiconst.UI_DISABLED, rotation=textRotation, labelClass=EveLabelLarge, rotationCenter=(0.5, 0.5))
        self.tabLabelCont.label.letterspace = 1
        frameCont = Transform(name='frameCont', parent=self, align=uiconst.TOALL, rotation=frameRotation)
        self.hilite = Frame(name='hilite', parent=frameCont, texturePath='res:/UI/Texture/Shared/sideTab_Over.png', align=uiconst.TOLEFT_NOPUSH, width=40, cornerSize=TABWIDTH)
        self.selectedFrame = Frame(name='selectedFrame', parent=frameCont, texturePath='res:/UI/Texture/Shared/sideTab_Over.png', align=uiconst.TOLEFT_NOPUSH, width=40, cornerSize=TABWIDTH, opacity=4.0)
        self.selectedFrame.display = False
        Frame(name='outputFrame', parent=frameCont, texturePath='res:/UI/Texture/Shared/sideTab_Active.png', align=uiconst.TOLEFT_NOPUSH, width=40, cornerSize=TABWIDTH, opacity=0.4)
        self.SetSelectedBtnState(self.isSelected)

    def GetRotations(self):
        textRotation = math.pi * 0.5
        if self.isLeftAlign:
            textRotation *= -1
            frameRotation = 0
        else:
            frameRotation = math.pi
        return (textRotation, frameRotation)

    def GetMinHeight(self):
        return self.tabLabelCont.label.textwidth + 40

    def OnClick(self, *args):
        self.onClick(self, self.args)

    def SetSelectedBtnState(self, isSelected):
        self.isSelected = isSelected
        if self.isSelected:
            self.selectedFrame.display = True
        else:
            self.selectedFrame.display = False


class SidePanelTabGroup(GridContainer):
    default_height = 100
    default_width = TABWIDTH
    default_lines = 2
    default_columns = 1
    default_isLeftAligned = True

    def ApplyAttributes(self, attributes):
        GridContainer.ApplyAttributes(self, attributes)
        self.isLeftAligned = attributes.get('isLeftAligned', self.default_isLeftAligned)
        self.selectedConfigName = attributes.selectedTab
        self.btnsDict = {}
        self.func = attributes.func
        tabBtnData = attributes.tabBtnData
        self.AddBtns(tabBtnData)

    def AddBtns(self, btnData):
        maxBtnHeight = 0
        self.Flush()
        self.btnsDict.clear()
        for eachData in btnData:
            tabText, configName, args = eachData
            isSelected = configName == self.selectedConfigName
            btn = SidePanelButtonWithText(parent=self, name=configName, configName=configName, tabText=tabText, align=uiconst.TOALL, opacity=1.0, onClick=self.OnBtnClicked, args=args, isLeftAlign=self.isLeftAligned, isSelected=isSelected)
            self.btnsDict[configName] = btn
            btnHeight = btn.GetMinHeight()
            maxBtnHeight = max(maxBtnHeight, btnHeight)

        numBtns = len(self.btnsDict)
        self.height = numBtns * maxBtnHeight
        self.lines = numBtns

    def OnBtnClicked(self, btn, args):
        if self.func:
            self.func(args)

    def SetSelectedBtn(self, configName):
        for eachConfigName, eachBtn in self.btnsDict.iteritems():
            if eachConfigName == configName:
                eachBtn.SetSelectedBtnState(True)
            else:
                eachBtn.SetSelectedBtnState(False)
