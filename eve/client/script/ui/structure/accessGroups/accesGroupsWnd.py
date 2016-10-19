#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\accessGroups\accesGroupsWnd.py
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import WndCaptionLabel
from eve.client.script.ui.control.eveSinglelineEdit import SinglelineEdit
from eve.client.script.ui.control.eveWindow import Window
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.client.script.ui.structure.accessGroups.accessGroupsController import AccessGroupsController
from eve.client.script.ui.structure.accessGroups.accessGroupListCont import GroupListCont
import carbonui.const as uiconst
from eve.client.script.ui.structure.accessGroups.groupCont import GroupCont
from eve.client.script.ui.structure.accessGroups.searchCont import SearchCont
from localization import GetByLabel

class AccessGroupsWnd(Window):
    default_captionLabelPath = 'UI/Structures/AccessGroups/GroupWndName'
    descriptionLabelPath = 'UI/Structures/AccessGroups/GroupsDescription'
    explanationLabelPath = 'UI/Structures/AccessGroups/GroupsExplanation'
    default_name = 'Groups window'
    default_windowID = 'GroupsWnd'
    default_width = 800
    default_height = 600
    default_minSize = (600, 400)
    default_iconNum = 'res:/UI/Texture/WindowIcons/accessGroups.png'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.SetWndIcon(self.iconNum, mainTop=-8)
        wndCaption = WndCaptionLabel(text=GetByLabel(self.default_captionLabelPath), parent=self.sr.topParent, align=uiconst.RELATIVE)
        left = wndCaption.left + wndCaption.textwidth + 4
        self.helpIcon = MoreInfoIcon(parent=self.sr.topParent, hint=GetByLabel(self.explanationLabelPath), left=left, top=10)
        if not settings.user.ui.Get('accessGroup_seenExtraInfo', False):
            self.helpIcon.ConstructGlow()
            uicore.animations.BlinkIn(self.helpIcon.bgGradient, startVal=0.1, endVal=0.5, duration=1.0, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_BOUNCE)
            self.helpIcon.OnMouseEnter = self.OnHelpIconMouseEnter
        self.controller = sm.GetService('structureControllers').GetAccessGroupController()
        self.mainCont = Container(name='mainCont', parent=self.sr.main, padding=4)
        self.searchCont = SearchCont(name='seachCont', parent=self.sr.topParent, align=uiconst.BOTTOMRIGHT, height=30, top=6, controller=self.controller)
        groupListParent = DragResizeCont(name='groupListCont', parent=self.mainCont, align=uiconst.TOLEFT_PROP, minSize=0.1, maxSize=0.5, defaultSize=0.5)
        self.groupCont = GroupCont(name='groupCont', parent=self.mainCont, padding=(0, 2, 0, 2), controller=self.controller)
        self.groupListCont = GroupListCont(name='groupListCont', parent=groupListParent, controller=self.controller)

    def OnHelpIconMouseEnter(self, *args):
        settings.user.ui.Set('accessGroup_seenExtraInfo', True)
        self.helpIcon.bgGradient.StopAnimations()
        MoreInfoIcon.OnMouseEnter(self.helpIcon, *args)
