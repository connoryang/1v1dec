#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\filterBtn.py
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.buttons import ButtonIcon
import carbonui.const as uiconst
import inventorycommon.const as invConst
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from localization import GetByLabel
NOT_SELECTED_FRAME_COLOR = (1, 1, 1, 0.1)
SELECTED_FRAME_COLOR = (1, 1, 1, 0.3)
BTN_TYPE_LOSLOT = 'loSlot'
BTN_TYPE_MEDSLOT = 'medSlot'
BTN_TYPE_HISLOT = 'hiSlot'
BTN_TYPE_RIGSLOT = 'rigSlot'
BTN_TYPE_DRONES = 'drones'
BTN_TYPE_SHIP = 'ship'
BTN_TYPE_RESOURCES = 'resources'
BTN_TYPE_SKILLS = 'skills'
BTN_TYPE_PERSONAL_FITTINGS = 'personalFittings'
BTN_TYPE_CORP_FITTINGS = 'corpFittings'

def AddHardwareButtons(*args, **kwargs):
    buttonData = ((BTN_TYPE_LOSLOT, 'res:/UI/Texture/classes/Fitting/filterIconLowSlot.png', 'UI/Fitting/FittingWindow/FilterLowSlot'),
     (BTN_TYPE_MEDSLOT, 'res:/UI/Texture/classes/Fitting/filterIconMediumSlot.png', 'UI/Fitting/FittingWindow/FilterMedSlot'),
     (BTN_TYPE_HISLOT, 'res:/UI/Texture/classes/Fitting/filterIconHighSlot.png', 'UI/Fitting/FittingWindow/FilterHiSlot'),
     (BTN_TYPE_RIGSLOT, 'res:/UI/Texture/classes/Fitting/filterIconRigSlot.png', 'UI/Fitting/FittingWindow/FilterRigSlot'),
     (BTN_TYPE_DRONES, 'res:/UI/Texture/classes/Fitting/filterIconDrones.png', 'UI/Fitting/FittingWindow/FilterDrones'),
     (BTN_TYPE_SHIP, 'res:/UI/Texture/classes/Fitting/tabFittings.png', 'UI/Fitting/FittingWindow/FilterCanShipUse'),
     (BTN_TYPE_RESOURCES, 'res:/UI/Texture/classes/Fitting/filterIconResources.png', 'UI/Fitting/FittingWindow/FilterResources'),
     (BTN_TYPE_SKILLS, 'res:/UI/Texture/classes/Fitting/filterIconSkills.png', 'UI/Fitting/FittingWindow/FilterSkills'))
    return AddFilterButtons(buttonData, *args, **kwargs)


def AddFittingFilterButtons(*args, **kwargs):
    buttonData = ((BTN_TYPE_PERSONAL_FITTINGS, 'res:/UI/Texture/WindowIcons/member.png', 'UI/Fitting/FittingWindow/FilterPersonalFittings'), (BTN_TYPE_CORP_FITTINGS, 'res:/UI/Texture/WindowIcons/corporation.png', 'UI/Fitting/FittingWindow/FilterCorpFittings'))
    return AddFilterButtons(buttonData, *args, **kwargs)


def AddFilterButtons(buttonData, parentCont, settingConfig, func, menuFunc = None, hintFunc = None, buttonSize = 30):
    btnDict = {}
    for buttonType, texturePath, labelPath in buttonData:
        btnSettingConfig = settingConfig % buttonType
        cont = FilterBtn(parent=parentCont, pos=(0,
         0,
         buttonSize,
         buttonSize), align=uiconst.NOALIGN, texturePath=texturePath, buttonType=buttonType, btnSettingConfig=btnSettingConfig, iconSize=buttonSize, func=func, args=(buttonType,), isChecked=settings.user.ui.Get(btnSettingConfig, False), menuFunc=menuFunc, hintFunc=hintFunc, hintLabelPath=labelPath)
        btnDict[buttonType] = cont

    return btnDict


def SetSettingForFilterBtns(flagID, btnDict):
    btnTypeToSelect = GetBtnTypeForFlagID(flagID)
    if btnTypeToSelect is None:
        return
    for btnType in (BTN_TYPE_LOSLOT,
     BTN_TYPE_MEDSLOT,
     BTN_TYPE_HISLOT,
     BTN_TYPE_RIGSLOT,
     BTN_TYPE_DRONES):
        btn = btnDict.get(btnType, None)
        if btn is None:
            continue
        if btnTypeToSelect == btnType:
            settings.user.ui.Set(btn.btnSettingConfig, True)
            btn.SetSelected()
        else:
            settings.user.ui.Set(btn.btnSettingConfig, False)
            btn.SetDeselected()


def GetBtnTypeForFlagID(flagID):
    if flagID in invConst.loSlotFlags:
        return BTN_TYPE_LOSLOT
    if flagID in invConst.medSlotFlags:
        return BTN_TYPE_MEDSLOT
    if flagID in invConst.hiSlotFlags:
        return BTN_TYPE_HISLOT
    if flagID in invConst.rigSlotFlags:
        return BTN_TYPE_RIGSLOT


class FilterBtn(ButtonIcon):
    default_colorSelected = (0.5, 0.5, 0.5, 0.1)
    checkmarkTexturePath = 'res:/ui/Texture/classes/Fitting/checkSmall.png'

    def ApplyAttributes(self, attributes):
        attributes.args = (self,) + attributes.args
        ButtonIcon.ApplyAttributes(self, attributes)
        self.loadingWheel = None
        self.menuFunc = attributes.menuFunc
        self.hintFunc = attributes.hintFunc
        self.hintLabelPath = attributes.hintLabelPath
        self.colorSelected = sm.GetService('uiColor').GetUIColor(uiconst.COLORTYPE_UIHILIGHT)
        self.checkmark = None
        self.buttonType = attributes.buttonType
        self.frame = Frame(bgParent=self, color=NOT_SELECTED_FRAME_COLOR)
        self.hint = self.buttonType
        self.btnSettingConfig = attributes.btnSettingConfig
        if attributes.isChecked:
            self.SetSelected()

    def OnClick(self, *args):
        if not self.enabled:
            return
        if self.isSelected:
            self.SetDeselected()
        else:
            self.SetSelected()
        ButtonIcon.OnClick(self, args)

    def SetSelected(self):
        ButtonIcon.SetSelected(self)
        self.ConstructCheckmark()
        self.checkmark.display = True
        self.frame.SetRGB(*SELECTED_FRAME_COLOR)

    def SetDeselected(self):
        ButtonIcon.SetDeselected(self)
        if self.checkmark:
            self.checkmark.display = False
        self.frame.SetRGB(*NOT_SELECTED_FRAME_COLOR)

    def ConstructCheckmark(self):
        if self.checkmark:
            return
        self.checkmark = Container(name='checkmark', parent=self, pos=(0, 0, 12, 12), align=uiconst.BOTTOMRIGHT, idx=0)
        Fill(bgParent=self.checkmark, color=self.colorSelected)
        Sprite(parent=self.checkmark, texturePath=self.checkmarkTexturePath, align=uiconst.CENTER, pos=(0, 0, 12, 12), state=uiconst.UI_DISABLED)

    def IsChecked(self):
        return bool(self.isSelected)

    def GetMenu(self):
        if self.menuFunc:
            return self.menuFunc(self)

    def ShowLoading(self):
        if not self.loadingWheel:
            self.loadingWheel = LoadingWheel(name='myLoadingWheel', parent=self, align=uiconst.CENTER, width=self.width * 1.5, height=self.height * 1.5, opacity=0.5)
        self.loadingWheel.display = True

    def HideLoading(self):
        if self.loadingWheel:
            self.loadingWheel.display = False

    def GetHint(self):
        if self.hintFunc:
            return self.hintFunc(self)
        return GetByLabel(self.hintLabelPath)
