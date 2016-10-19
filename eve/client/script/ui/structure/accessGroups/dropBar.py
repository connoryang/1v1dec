#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\accessGroups\dropBar.py
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.structure.accessGroups.ownerGroupUtils import GetOwnerIDsAndMembershipTypeFromNodes
from localization import GetByLabel
from ownergroups.ownergroupsUIUtil import ACCESS_SORT_ORDER, GetChangeRestrictions, GetMembershipTypeTextureAndLabelPaths, GetMembershipSortIdx, GetSetAsMembershipLabelPaths
FILL_IDLE_OPACITY = 0.5
DRAGGING_OPACITY = 1.0
HILITE_OPACITY = 0.6
PADDING = 2
MOUSE_EXIT = 0
MOUSE_ENTER = 1
MOUSE_DROP_ON = 2

class DropCont(Container):
    default_height = 80
    __notifyevents__ = ['OnExternalDragInitiated', 'OnExternalDragEnded']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        controller = attributes.controller
        self.ConstructUI(controller)
        sm.RegisterNotify(self)

    def ConstructUI(self, controller):
        self.dropGridCont = DropBar(parent=self, align=uiconst.TOTOP, controller=controller, height=36, mouseCallback=self.DropContMouseCallback)
        arrowPos = (0,
         self.dropGridCont.top + self.dropGridCont.height - 2,
         18,
         8)
        self.arrow = Sprite(parent=self, align=uiconst.TOPLEFT, pos=arrowPos, texturePath='res:/UI/Texture/classes/AccessGroups/arrow.png')
        arrowColor = sm.GetService('uiColor').GetUIColor(uiconst.COLORTYPE_UIHILIGHT)
        self.arrow.SetRGBA(arrowColor[0], arrowColor[1], arrowColor[2], HILITE_OPACITY)
        self.arrow.display = False
        self.dropTextCont = Container(name='dropOverlay', parent=self, align=uiconst.TOTOP, height=32, padding=(1, 6, 1, 0), state=uiconst.UI_DISABLED)
        dropText = GetByLabel('UI/Structures/AccessGroups/DropMembers')
        self.dropLabel = EveLabelMedium(name='dropLabel', parent=self.dropTextCont, text=dropText, padLeft=10, align=uiconst.CENTER)
        self.colorFill = FillThemeColored(name='colorFill', bgParent=self.dropTextCont, padding=(1, 0, 1, 1), colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.0)
        self.bgFill = FillThemeColored(name='bgFill', bgParent=self.dropTextCont, padding=(1, 0, 1, 1), colorType=uiconst.COLORTYPE_UIBASECONTRAST, opacity=FILL_IDLE_OPACITY)

    def DropContMouseCallback(self, mouseAction, membershipType, numNodes = 0):
        if mouseAction == MOUSE_DROP_ON:
            BlinkInAndOut(self.colorFill)
            self.dropLabel.text = GetByLabel('UI/Structures/AccessGroups/DropMembers')
            return
        if not uicore.IsDragging():
            return
        if mouseAction == MOUSE_ENTER:
            labelPath = GetSetAsMembershipLabelPaths(membershipType)
            self.MoveArrow(membershipType)
            FadeObject(self.colorFill, endValue=HILITE_OPACITY)
            FadeObject(self.arrow, endValue=HILITE_OPACITY)
            FadeObjectOut(self.bgFill)
        else:
            labelPath = 'UI/Structures/AccessGroups/DropMembers'
            self.arrow.display = False
            FadeObject(self.bgFill, endValue=DRAGGING_OPACITY)
            FadeObjectOut(self.colorFill)
        self.dropLabel.text = GetByLabel(labelPath, numMembers=numNodes)

    def MoveArrow(self, membershipType):
        w = self.dropTextCont.renderObject.displayWidth
        step = float(w) / (2 * len(ACCESS_SORT_ORDER))
        membershipIdx = GetMembershipSortIdx(membershipType)
        offset = int((1 + 2 * membershipIdx) * step - self.arrow.width / 2.0)
        uicore.animations.MorphScalar(self.arrow, 'left', startVal=self.arrow.left, endVal=offset, duration=0.2)
        self.arrow.display = True

    def OnExternalDragInitiated(self, dragSource, dragData):
        membershipTypesByMemberID = GetOwnerIDsAndMembershipTypeFromNodes(dragData)
        if membershipTypesByMemberID:
            self.dropGridCont.ExternalDragInitiated(dragSource, dragData, numNodes=len(membershipTypesByMemberID))
            FadeObject(self.bgFill, endValue=DRAGGING_OPACITY)

    def OnExternalDragEnded(self, *args):
        self.dropGridCont.ExternalDragEnded()
        FadeObject(self.bgFill, endValue=FILL_IDLE_OPACITY)
        FadeObjectOut(self.arrow)
        FadeObjectOut(self.colorFill)


class DropBar(GridContainer):
    default_lines = 1
    default_height = 32
    default_name = 'dropGridCont'
    default_columns = len(ACCESS_SORT_ORDER)

    def ApplyAttributes(self, attributes):
        GridContainer.ApplyAttributes(self, attributes)
        self.parentMouseCallback = attributes.mouseCallback
        self.currentGroupID = attributes.currentGroupID
        self.controller = attributes.controller
        self.dropContainers = {}
        for membershipType in ACCESS_SORT_ORDER:
            texturePath, hintPath = GetMembershipTypeTextureAndLabelPaths(membershipType)
            d = DropContainer(parent=self, texturePath=texturePath, membershipType=membershipType, controller=self.controller, currentGroupID=self.currentGroupID, hintPath=hintPath, dropCallback=self.AddGroupMembersWithMembershipType, mouseCallback=self.MouseCallback, padding=PADDING)
            self.dropContainers[membershipType] = d

        self.dropOverlay = Container(name='dropOverlay', parent=self, align=uiconst.TOBOTTOM, height=32, state=uiconst.UI_DISABLED)

    def SetCurrentGroupID(self, groupID, membershipType):
        self.currentGroupID = groupID
        accessRestrictions = GetChangeRestrictions(membershipType)
        for membershipType, cont in self.dropContainers.iteritems():
            cont.SetDisableStatus(membershipType in accessRestrictions)

    def AddGroupMembersWithMembershipType(self, memberIDs, membershipType):
        self.controller.SetGroupMembersWithSameRight(self.currentGroupID, memberIDs, membershipType)

    def ExternalDragInitiated(self, dragSource, dragData, numNodes):
        for eachCont in self.dropContainers.itervalues():
            eachCont.ExternalDragInitiated(dragSource, dragData, numNodes)

    def ExternalDragEnded(self, *args):
        for eachCont in self.dropContainers.itervalues():
            eachCont.ExternalDragEnded()

    def MouseCallback(self, mouseAction, membershipType, numNodes):
        self.parentMouseCallback(mouseAction, membershipType, numNodes)


class DropContainer(Container):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.mouseCallback = attributes.mouseCallback
        self.validDragNodes = 0
        self.colorFill = FillThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.0)
        self.bgFill = FillThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIBASECONTRAST, opacity=FILL_IDLE_OPACITY)
        texturePath = attributes.texturePath
        self.membershipType = attributes.membershipType
        self.dropCallback = attributes.dropCallback
        self.isDisabled = False
        self.icon = GlowSprite(parent=self, align=uiconst.CENTER, pos=(0, 0, 24, 24), texturePath=texturePath, state=uiconst.UI_DISABLED)
        self.hint = GetByLabel(attributes.hintPath)

    def ExternalDragInitiated(self, dragSource, dragData, numNodes):
        if self.isDisabled:
            return
        self.validDragNodes = numNodes
        self.FadeBgFill(endValue=DRAGGING_OPACITY)

    def ExternalDragEnded(self, *args):
        if self.isDisabled:
            return
        self.validDragNodes = 0
        self.FadeBgFill(endValue=FILL_IDLE_OPACITY)

    def FadeBgFill(self, endValue):
        FadeObject(self.bgFill, endValue=endValue)
        FadeObject(self.icon, endValue=endValue)

    def MouseOverCont(self):
        if self.isDisabled or not self.validDragNodes:
            return
        self.icon.OnMouseEnter()
        if uicore.IsDragging():
            FadeObject(self.colorFill, endValue=HILITE_OPACITY)
            FadeObjectOut(self.bgFill)
            self.mouseCallback(MOUSE_ENTER, self.membershipType, self.validDragNodes)

    def MouseExitCont(self):
        if self.isDisabled or not self.validDragNodes:
            return
        FadeObjectOut(self.colorFill)
        if uicore.IsDragging():
            bgEndValue = DRAGGING_OPACITY
        else:
            bgEndValue = FILL_IDLE_OPACITY
        self.icon.OnMouseExit()
        FadeObject(self.bgFill, endValue=bgEndValue)
        self.mouseCallback(MOUSE_EXIT, self.membershipType, 0)

    def OnMouseEnter(self, *args):
        self.MouseOverCont()

    def OnMouseExit(self, *args):
        self.MouseExitCont()

    def OnDragEnter(self, dragObj, nodes):
        self.MouseOverCont()

    def OnDragExit(self, *args):
        self.MouseExitCont()

    def OnDropData(self, dragSource, nodes):
        if self.isDisabled:
            return
        membershipTypesByMemberID = GetOwnerIDsAndMembershipTypeFromNodes(nodes)
        if not membershipTypesByMemberID:
            return
        memberIDs = membershipTypesByMemberID.keys()
        self.dropCallback(memberIDs, self.membershipType)
        BlinkInAndOut(object=self.colorFill)
        self.mouseCallback(MOUSE_DROP_ON, self.membershipType, 0)

    def SetDisableStatus(self, isDisabled):
        self.isDisabled = isDisabled
        if isDisabled:
            self.icon.opacity = 0.1
            self.bgFill.opacity = 0.05
        else:
            self.icon.opacity = FILL_IDLE_OPACITY
            self.bgFill.opacity = FILL_IDLE_OPACITY


def BlinkInAndOut(object):
    uicore.animations.BlinkIn(object, startVal=0.0, endVal=0.5, loops=1, duration=0.25, curveType=uiconst.ANIM_BOUNCE)


def FadeObjectOut(object):
    FadeObject(object, endValue=0.0)


def FadeObject(object, endValue = 1.0):
    uicore.animations.FadeTo(object, startVal=object.opacity, endVal=endValue, duration=0.25)
