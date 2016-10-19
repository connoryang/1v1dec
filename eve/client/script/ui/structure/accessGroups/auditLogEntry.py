#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\accessGroups\auditLogEntry.py
from carbon.common.script.util.format import FmtDate
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbonui.control.menuLabel import MenuLabel
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from localization import GetByLabel
from ownergroups.ownergroupConst import GROUP_NAME_CHANGED, GROUP_DESCRIPTION_CHANGED, GROUP_CREATED, GROUP_DELETED, PUBLIC_MEMBER_ID
from ownergroups.ownergroupsUIUtil import TEXTS_AND_ICONS_FOR_MEMBERC_CHANGES
from sovDashboard.sovStatusEntries import MouseInsideScrollEntry
import carbonui.const as uiconst
import blue

class AuditLogEntryBase(MouseInsideScrollEntry):
    default_name = 'AuditLogEntry'
    changeIconSize = 32
    ENTRYHEIGHT = 36

    def ApplyAttributes(self, attributes):
        MouseInsideScrollEntry.ApplyAttributes(self, attributes)
        self.node = attributes.node
        self.ConstructUI()

    def ConstructUI(self):
        self.changeSprite = Sprite(name='changeSprite', parent=self, align=uiconst.CENTERLEFT, pos=(4, 0, 20, 20))
        labelLeft = self.changeSprite.left + self.changeSprite.width + 10
        self.logLabel = EveLabelMedium(name='logLabel', parent=self, left=labelLeft, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)

    def Load(self, node):
        timeStamp = FmtDate(node.eventInfo.logDate)
        text, texturePath = self.GetTextAndTextureForEvent(node.eventInfo)
        self.logLabel.text = '  '.join([timeStamp, text])
        self.changeSprite.SetTexturePath(texturePath)

    def OnClick(self, *args):
        self.sr.node.scroll.SelectNode(self.sr.node)

    def GetMenu(self):
        return []

    @classmethod
    def GetTextAndTextureForEvent(cls, eventInfo):
        return ('', '')

    @classmethod
    def GetCopyData(cls, node):
        timeStamp = FmtDate(node.eventInfo.logDate)
        text, texturePath = cls.GetTextAndTextureForEvent(node.eventInfo)
        eventText = node.eventInfo.newText or ''
        return '<t>'.join([timeStamp, text, eventText])


class AuditLogGroupChanges(AuditLogEntryBase):

    def ApplyAttributes(self, attributes):
        AuditLogEntryBase.ApplyAttributes(self, attributes)

    @classmethod
    def GetTextAndTextureForEvent(cls, eventInfo):
        charText = GetLinkForCharacter(eventInfo.characterID)
        if eventInfo.actionID == GROUP_CREATED:
            return (GetByLabel('UI/Structures/LoggedChanges/GroupCreated', actorName=charText), 'res:/UI/Texture/classes/AccessGroups/groupCreated.png')
        if eventInfo.actionID == GROUP_DELETED:
            return (GetByLabel('UI/Structures/LoggedChanges/GroupDeleted', actorName=charText), '')
        return ('', '')


class AuditLogChangedText(AuditLogEntryBase):

    def ApplyAttributes(self, attributes):
        AuditLogEntryBase.ApplyAttributes(self, attributes)

    def Load(self, node):
        AuditLogEntryBase.Load(self, node)
        eventInfo = node.eventInfo
        if eventInfo.actionID == GROUP_NAME_CHANGED:
            labelPath = 'UI/Structures/LoggedChanges/DescriptionChangedHint'
        elif eventInfo.actionID == GROUP_DESCRIPTION_CHANGED:
            labelPath = 'UI/Structures/LoggedChanges/NameChangedHint'
        else:
            return
        self.hint = GetByLabel(labelPath, oldText=eventInfo.oldText, newText=eventInfo.newText)

    def GetMenu(self):
        eventInfo = self.node.eventInfo
        if eventInfo.actionID == GROUP_NAME_CHANGED:
            labelPath = 'UI/Structures/LoggedChanges/CopyOldName'
        elif eventInfo.actionID == GROUP_DESCRIPTION_CHANGED:
            labelPath = 'UI/Structures/LoggedChanges/CopyOldDescription'
        else:
            return []
        m = [(MenuLabel(labelPath), self.CopyOldText, ())]
        return m

    def CopyOldText(self):
        oldText = self.node.eventInfo.oldText
        blue.pyos.SetClipboardData(oldText)

    @classmethod
    def GetTextAndTextureForEvent(cls, eventInfo):
        charText = GetLinkForCharacter(eventInfo.characterID)
        if eventInfo.actionID == GROUP_NAME_CHANGED:
            labelText = GetByLabel('UI/Structures/LoggedChanges/GroupNameChanged', actorName=charText)
        elif eventInfo.actionID == GROUP_DESCRIPTION_CHANGED:
            labelText = GetByLabel('UI/Structures/LoggedChanges/GroupDescriptionChanged', actorName=charText)
        else:
            return ('', '')
        texturePath = 'res:/UI/Texture/classes/AccessGroups/nameDescChanged.png'
        return (labelText, texturePath)


class AuditLogMemberChanges(AuditLogEntryBase):

    @classmethod
    def GetTextAndTextureForEvent(cls, eventInfo):
        keyTuple = (eventInfo.oldMembershipType, eventInfo.newMembershipType)
        labelPath, iconPath = TEXTS_AND_ICONS_FOR_MEMBERC_CHANGES.get(keyTuple, (None, None))
        if labelPath is None:
            return ('', '')
        charText = GetLinkForCharacter(eventInfo.characterID)
        if eventInfo.ownerID:
            changedText = GetLinkForCharacter(eventInfo.ownerID)
        elif eventInfo.ownerID == PUBLIC_MEMBER_ID:
            changedText = "'%s'" % GetByLabel('UI/Structures/AccessGroups/PublicUser')
        else:
            changedText = ''
        labelText = GetByLabel(labelPath, actorName=charText, changedName=changedText)
        return (labelText, iconPath)


def GetLinkForCharacter(charID):
    charInfo = cfg.eveowners.Get(charID)
    charText = GetShowInfoLink(charInfo.typeID, charInfo.name, itemID=charID)
    return charText
