#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\accessGroups\auditLogCont.py
from carbonui.primitives.container import Container
from carbonui.util.bunch import Bunch
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.structure.accessGroups.auditLogEntry import AuditLogEntryBase, AuditLogChangedText, AuditLogMemberChanges, AuditLogGroupChanges
from eve.client.script.ui.structure.accessGroups.ownerGroupUtils import ConvertDBRowToBundle
from ownergroups.ownergroupConst import GROUP_CREATED, GROUP_DELETED, GROUP_NAME_CHANGED, GROUP_DESCRIPTION_CHANGED, GROUP_MEMBER_REMOVED, GROUP_MEMBER_ADDED, GROUP_MEMBERTYPE_CHANGED

class AuditLogCont(Container):
    entryDict = {GROUP_CREATED: AuditLogGroupChanges,
     GROUP_DELETED: AuditLogGroupChanges,
     GROUP_MEMBER_ADDED: AuditLogMemberChanges,
     GROUP_MEMBERTYPE_CHANGED: AuditLogMemberChanges,
     GROUP_MEMBER_REMOVED: AuditLogMemberChanges,
     GROUP_NAME_CHANGED: AuditLogChangedText,
     GROUP_DESCRIPTION_CHANGED: AuditLogChangedText}

    def ApplyAttributes(self, attributes):
        self.currentGroupID = None
        Container.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.scroll = Scroll(name='auditLogScroll', parent=self)

    def LoadGroup(self, groupID):
        self.currentGroupID = groupID
        self.LoadAuditLog()

    def LoadAuditLog(self):
        groupLogs = self.controller.GetGroupLogs(self.currentGroupID)
        nodes = []
        for eachEvent in groupLogs:
            eventBundle = ConvertDBRowToBundle(eachEvent)
            decoClasss = self.GetEntryClass(eventBundle.actionID)
            node = Bunch(decoClass=decoClasss, controller=self.controller, eventInfo=eventBundle)
            nodes.append(node)

        self.scroll.Load(contentList=nodes)

    def GetEntryClass(self, actionID):
        return self.entryDict.get(actionID, AuditLogEntryBase)
