#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\shipHud\groupAllIcon.py
from eve.client.script.ui.control.eveIcon import Icon
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from localization import GetByLabel
import uthread
import blue

class GroupAllIcon(Icon):
    default_left = 0
    default_top = 0
    default_width = 16
    default_height = 16
    default_state = uiconst.UI_HIDDEN
    default_icon = 'ui_73_16_251'
    default_name = 'groupAllIcon'

    def ApplyAttributes(self, attributes):
        Icon.ApplyAttributes(self, attributes)
        self.orgPos = self.top

    def OnClick(self, *args):
        if settings.user.ui.Get('lockModules', 0):
            return
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        if dogmaLocation.CanGroupAll(session.shipid):
            dogmaLocation.LinkAllWeapons(session.shipid)
        else:
            dogmaLocation.UnlinkAllWeapons(session.shipid)

    def OnMouseDown(self, *args):
        self.top = self.orgPos + 1

    def OnMouseUp(self, *args):
        self.top = self.orgPos

    def OnMouseExit(self, *args):
        self.top = self.orgPos


class GroupAllButton(Container):
    __notifyevents__ = ['OnAttributes', 'OnRefreshModuleBanks']
    default_left = 0
    default_top = 9
    default_width = 16
    default_height = 16
    default_name = 'GroupAllButton'
    default_align = uiconst.TOPLEFT
    groupAllIconID = 'ui_73_16_252'
    ungroupAllIconID = 'ui_73_16_251'
    groupAllLabelPath = 'UI/Inflight/GroupAllWeapons'
    ungroupAllLabelPath = 'UI/Inflight/UngroupAllWeapons'
    lockeLabelPath = 'UI/Inflight/Locked'

    def ApplyAttributes(self, attributes):
        self.updateGroupAllButtonThread = None
        Container.ApplyAttributes(self, attributes)
        self.groupAllIcon = GroupAllIcon(parent=self, idx=0)
        sm.RegisterNotify(self)
        self.CheckGroupAllButton()

    def CheckGroupAllButton(self):
        if self.destroyed:
            return
        icon = self.groupAllIcon
        if icon is None or icon.destroyed:
            return
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        for typeID, qty in dogmaLocation.GetGroupableTypes(session.shipid).iteritems():
            if qty > 1:
                break
        else:
            icon.state = uiconst.UI_HIDDEN
            return

        icon.state = uiconst.UI_NORMAL
        if dogmaLocation.CanGroupAll(session.shipid):
            iconID = self.groupAllIconID
            hintPath = self.groupAllLabelPath
        else:
            iconID = self.ungroupAllIconID
            hintPath = self.ungroupAllLabelPath
        icon.LoadIcon(iconID)
        hint = GetByLabel(hintPath)
        if settings.user.ui.Get('lockModules', False):
            hint = GetByLabel(self.lockeLabelPath, unit=hint)
        icon.hint = hint
        if getattr(self, 'updateGroupAllButtonThread', None):
            self.updateGroupAllButtonThread.kill()
        self.updateGroupAllButtonThread = uthread.new(self.UpdateGroupAllButton)

    def UpdateGroupAllButton(self):
        if self.destroyed:
            return
        GetOpacity = sm.GetService('clientDogmaIM').GetDogmaLocation().GetGroupAllOpacity
        if sm.GetService('clientDogmaIM').GetDogmaLocation().CanGroupAll(session.shipid):
            attributeName = 'lastGroupAllRequest'
        else:
            attributeName = 'lastUngroupAllRequest'
        icon = self.groupAllIcon
        if icon is None or icon.destroyed:
            return
        icon.state = uiconst.UI_DISABLED
        while True:
            opacity = GetOpacity(attributeName)
            if opacity > 0.999:
                break
            icon.color.a = 0.2 + opacity * 0.6
            blue.pyos.synchro.Yield()
            if self.destroyed:
                return

        icon.color.a = 1.0
        icon.state = uiconst.UI_NORMAL

    def OnAttributes(self, ch):
        for each in ch:
            if each[0] == 'isOnline':
                self.CheckGroupAllButton()
                break

    def OnRefreshModuleBanks(self):
        self.CheckGroupAllButton()
