#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\accessGroups\addCont.py
from carbonui.primitives.container import Container
from eve.client.script.ui.control.buttons import ButtonIcon, Button
import carbonui.const as uiconst
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.control.eveWindowUnderlay import RaisedUnderlay
from eve.client.script.ui.control.themeColored import FillThemeColored, FrameThemeColored
from eve.client.script.ui.structure.accessGroups.nameAndDescriptionWnd import AccessGroupsCreateWnd
from eve.client.script.ui.shared.neocom.ownerSearch import OwnerSearchWindow
from localization import GetByLabel

class AddCont(Container):
    default_height = 30
    default_align = uiconst.TOBOTTOM
    default_clipChildren = True
    tooltipPath = ''
    default_padBottom = 4
    default_state = uiconst.UI_NORMAL
    texturePath = 'res:/UI/Texture/Icons/Plus_Small.png'
    iconSize = 12

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.btnUnderlay = RaisedUnderlay(bgParent=self, isGlowEdgeRotated=True)
        self.createBtn = ButtonIcon(name='addBtn', parent=self, align=uiconst.CENTERLEFT, pos=(0, 0, 30, 30), iconSize=self.iconSize, texturePath=self.texturePath, hint=GetByLabel(self.tooltipPath), state=uiconst.UI_DISABLED)
        self.createNewLabel = EveLabelLarge(name='createNewLabel', parent=self, text='', align=uiconst.CENTERLEFT, left=34)

    def OnAddEntry(self, *args):
        pass

    def OnMouseEnter(self, *args):
        self.btnUnderlay.OnMouseEnter()
        uicore.animations.MorphScalar(self.createBtn.icon, 'glowAmount', self.createBtn.icon.glowAmount, ButtonIcon.OPACITY_MOUSEHOVER, duration=0.2)

    def OnMouseExit(self, *args):
        self.btnUnderlay.OnMouseExit()
        uicore.animations.MorphScalar(self.createBtn.icon, 'glowAmount', self.createBtn.icon.glowAmount, 0.0, duration=0.2)

    def OnClick(self, *args):
        self.OnAddEntry()
        uicore.animations.MorphScalar(self.createBtn.icon, 'glowAmount', self.createBtn.icon.glowAmount, ButtonIcon.OPACITY_MOUSECLICK, duration=0.2, curveType=uiconst.ANIM_BOUNCE)

    def OnMouseDown(self, *args):
        self.FadeUnderlay(toValue=1.5)

    def OnMouseUp(self, *args):
        self.FadeUnderlay(toValue=1.0)

    def FadeUnderlay(self, toValue):
        uicore.animations.FadeTo(self.btnUnderlay, self.btnUnderlay.opacity, toValue, duration=0.1)


class AddGroupCont(AddCont):
    default_name = 'AddGroupCont'
    tooltipPath = 'UI/Structures/AccessGroups/CreateNewGroup'

    def ApplyAttributes(self, attributes):
        AddCont.ApplyAttributes(self, attributes)
        self.createNewLabel.text = GetByLabel('UI/Structures/AccessGroups/NewGroup')

    def OnAddEntry(self, *args):
        AccessGroupsCreateWnd.Open(controller=self.controller)


class AddMemberCont(AddCont):
    default_name = 'AddMemberCont'
    tooltipPath = 'UI/Structures/AccessGroups/AddMembers'

    def ApplyAttributes(self, attributes):
        AddCont.ApplyAttributes(self, attributes)
        self.createNewLabel.text = GetByLabel('UI/Structures/AccessGroups/AddMembers')
        self.func = attributes.func

    def OnAddEntry(self, *args):
        OwnerSearchWindow.CloseIfOpen(windowID='AccessGroupsAddMember')
        OwnerSearchWindow.Open(windowID='AccessGroupsAddMember', actionBtns=[(GetByLabel('UI/Structures/AccessGroups/AddMembers'), self.AddMembers, True)], caption=GetByLabel('UI/Structures/AccessGroups/AddMembers'), input='', showContactList=True, multiSelect=True, ownerGroups=[const.groupCharacter, const.groupCorporation, const.groupAlliance])

    def AddMembers(self, results):
        OwnerSearchWindow.CloseIfOpen(windowID='AccessGroupsAddMember')
        self.func([ row.itemID for row in results() ])


class AddPublic(AddCont):
    default_name = 'AddMemberCont'
    tooltipPath = 'UI/Structures/AccessGroups/AddMembers'
    texturePath = 'res:/UI/Texture/classes/AccessGroups/browser.png'
    default_width = 30
    default_align = uiconst.TORIGHT
    default_padBottom = 4
    default_state = uiconst.UI_NORMAL
    iconSize = 30

    def ApplyAttributes(self, attributes):
        AddCont.ApplyAttributes(self, attributes)
        self.hint = GetByLabel('UI/Structures/AccessGroups/AddPublic')
        self.func = attributes.func

    def OnAddEntry(self, *args):
        self.func()
