#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\accessGroups\accessGroupsController.py
from eve.client.script.ui.structure.accessGroups.menuProvider import MenuProvider
from eve.client.script.ui.structure.accessGroups.ownerGroupUtils import GetMemberIDsToUpdate, GetMembershipTypeByMemberID
from localization import GetByLabel
from signals import Signal
import ownergroups.ownergroupConst as ownergroupConst
from ownergroups.ownergroupsUIUtil import GetTextForWarning
import carbonui.const as uiconst
import util
REMOTE_SERVICE_NAME = 'ownerGroupManager'

class AccessGroupsController(object):
    __notifyevents__ = ['OnOwnerGroupsUpdated']

    def __init__(self):
        sm.RegisterNotify(self)
        self.remoteSvc = sm.RemoteSvc(REMOTE_SERVICE_NAME)
        self.objectCashingSvc = sm.GetService('objectCaching')
        self.on_new_group_created = Signal()
        self.on_group_selected = Signal()
        self.on_groupmembers_changed = Signal()
        self.on_groupmembers_removed = Signal()
        self.on_group_deleted = Signal()
        self.on_group_updated = Signal()
        self.on_groups_reload = Signal()
        self.membersByGroupID = {}
        self.groupByGroupID = None
        self.publicGroupsByGroupID = {}
        self.myGroupsCacheInvalidated = False
        self.currentSearchResults = None

    def GetGroupLogs(self, groupID):
        if groupID not in self.groupByGroupID or self.groupByGroupID[groupID].creatorID != session.corpid:
            return self.remoteSvc.GetGroupLogs(groupID)
        return []

    def GetMembers(self, groupID, noServerTrips = False):
        if groupID in self.membersByGroupID or noServerTrips:
            return self.membersByGroupID.get(groupID, None)
        members = self.remoteSvc.GetMembers(groupID)
        membershipTypeByMemberID = GetMembershipTypeByMemberID(members)
        self.membersByGroupID[groupID] = membershipTypeByMemberID
        return membershipTypeByMemberID

    def UpdateMemberCache(self, groupID, updateDict):
        self.UpdateClientCache(groupID, self.membersByGroupID, updateDict)

    def UpdateClientCache(self, groupID, cacheDict, updateDict):
        cacheForGroup = cacheDict.get(groupID)
        if cacheForGroup is None:
            return
        cacheForGroup.update(updateDict)

    def RemoveFromMemberCache(self, groupID, membersToRemove):
        membershipTypeByMemberID = self.membersByGroupID.get(groupID, None)
        if membershipTypeByMemberID is None:
            return
        for memberID in membersToRemove:
            membershipTypeByMemberID.pop(memberID, None)

    def GetAllMyMemberIDs(self):
        allMemberIDs = set()
        groupIDsToFetch = set()
        for eachGroupID in self.GetMyGroups():
            groupMembers = self.GetMembers(eachGroupID, noServerTrips=True)
            if groupMembers:
                allMemberIDs.update(groupMembers.keys())
            else:
                groupIDsToFetch.add(eachGroupID)

        if groupIDsToFetch:
            memberIDsInGroups, updateDict = self._GetUncachedMembers(groupIDsToFetch)
            allMemberIDs.update(memberIDsInGroups)
            self.membersByGroupID.update(updateDict)
        allMemberIDsByGroupID = self.membersByGroupID.copy()
        return (allMemberIDsByGroupID, allMemberIDs)

    def _GetUncachedMembers(self, groupIDsToFetch):
        uncachedMembersByGroupIDs = self.remoteSvc.GetMembersForMultipleGroups(list(groupIDsToFetch))
        updateDict = {}
        memberIDsInGroups = set()
        for groupID, members in uncachedMembersByGroupIDs.iteritems():
            membershipTypeByMemberID = GetMembershipTypeByMemberID(members)
            updateDict[groupID] = membershipTypeByMemberID

        return (memberIDsInGroups, updateDict)

    def GetMyGroups(self):
        if self.groupByGroupID is None:
            self.groupByGroupID = {g.groupID:g for g in self.remoteSvc.GetMyGroups()}
        return self.groupByGroupID

    def UpdatGroupCache(self, groupID, updateDict):
        self.UpdateClientCache(groupID, self.groupByGroupID, updateDict)

    def GetMyGroupInfo(self, groupID):
        myGroups = self.GetMyGroups()
        return myGroups.get(groupID)

    def IsGroupCorpOwned(self, groupID):
        groupInfo = self.GetMyGroupInfo(groupID)
        if groupInfo:
            return groupInfo.creatorID == session.corpid
        return False

    def OnCreateGroup(self, name, description):
        self.Create(name, description)
        self.InvalidateGetMyGroups()
        self.on_new_group_created()

    def Create(self, name, description):
        return self.remoteSvc.Create(name, description)

    def SelectGroup(self, groupID, sendSignal = True):
        settings.user.ui.Set('accessGroup_lastGroup', groupID)
        if sendSignal:
            self.on_group_selected(groupID)

    def GetSelectedGroupID(self):
        return settings.user.ui.Get('accessGroup_lastGroup', None)

    def EditGroupNameAndDescription(self, groupID, newName, newDesc):
        self.remoteSvc.UpdateName(groupID, newName)
        self.remoteSvc.UpdateDescription(groupID, newDesc)
        self.UpdatGroupCache(groupID, updateDict={'name': newName,
         'description': newDesc})
        self.on_group_updated(groupID)

    def Delete(self, groupID):
        group = self.GetMyGroupInfo(groupID)
        ret = eve.Message('AccessGroupDeleteGroup', {'groupName': group.name}, uiconst.YESNO)
        if ret != uiconst.ID_YES:
            return
        self.remoteSvc.Delete(groupID)
        self.groupByGroupID.pop(groupID, None)
        self.on_group_deleted()

    def GetGroupInfoFromID(self, groupID, fetchToServer = False):
        groupInfo = self.GetMyGroupInfo(groupID)
        if groupInfo:
            return groupInfo
        if groupID in self.publicGroupsByGroupID:
            return self.publicGroupsByGroupID[groupID]
        if not fetchToServer:
            return None
        return self.remoteSvc.GetGroup(groupID)

    def PopulatePublicGroupInfo(self, groupIDs, forceFetchInfoForPublicGroup = False):
        self.GetMyGroups()
        groupIDsToFetch = [ gID for gID in groupIDs if gID not in self.groupByGroupID and (forceFetchInfoForPublicGroup or gID not in self.publicGroupsByGroupID) ]
        if not groupIDsToFetch:
            return
        if forceFetchInfoForPublicGroup:
            for gID in groupIDsToFetch:
                self.publicGroupsByGroupID.pop(gID, None)

        for group in self.remoteSvc.GetGroupsMany(groupIDsToFetch):
            self.publicGroupsByGroupID[group.groupID] = group

    def AddPublicMember(self, groupID):
        return self.AddMembers(groupID, {ownergroupConst.PUBLIC_MEMBER_ID: ownergroupConst.MEMBERSHIP_TYPE_MEMBER})

    def AddMembers(self, groupID, membershipTypeByMemberIDs, silently = False):
        failedToAdd = []
        currentMembers = self.GetMembers(groupID)
        membersToAdd = {}
        if self.IsGroupCorpOwned(groupID):
            return membershipTypeByMemberIDs.keys()
        for memberID, membershipType in membershipTypeByMemberIDs.iteritems():
            if memberID not in currentMembers:
                membersToAdd[memberID] = membershipType

        if membersToAdd:
            failedToAdd = self.remoteSvc.AddMembers(groupID, membersToAdd)
            failedMemberIDs = {x[0] for x in failedToAdd}
            membersToUpdate = {x:y for x, y in membersToAdd.iteritems() if x not in failedMemberIDs}
            if not silently:
                self.DisplayWarningIfNeeded(failedInfo=failedToAdd)
                self.UpdateMemberCache(groupID, membersToUpdate)
                self.on_groupmembers_changed(groupID)
        return failedToAdd

    def UpdateMembershipTypes(self, groupID, memberIDs, membershipType, silently = False):
        failedToChange = []
        if session.charid in memberIDs:
            cancelChange = self.CancelChangeBecauseOfDemotingYourself(groupID, membershipType)
            if cancelChange:
                memberIDs.remove(session.charid)
                failedToChange.append((session.charid, 'NotDemotingYourself'))
        if not memberIDs:
            return failedToChange
        groupMembers = self.GetMembers(groupID)
        memberIDsToChange = [ mID for mID in memberIDs if groupMembers.get(mID, None) != membershipType ]
        if not memberIDsToChange:
            return failedToChange
        failedToChange += self.remoteSvc.UpdateMembershipTypes(groupID, memberIDsToChange, membershipType)
        membersToUpdate = self.GetUpdateMemberDict(memberIDsToChange, membershipType, failedToChange)
        self.UpdateMemberCache(groupID, membersToUpdate)
        if not silently:
            self.DisplayWarningIfNeeded(failedInfo=failedToChange)
            self.on_groupmembers_changed(groupID)
        return failedToChange

    def CancelChangeBecauseOfDemotingYourself(self, groupID, newRight):
        group = self.GetMyGroupInfo(groupID)
        accessRight = group.membershipType
        if accessRight == ownergroupConst.MEMBERSHIP_TYPE_ADMIN and newRight != ownergroupConst.MEMBERSHIP_TYPE_ADMIN:
            if eve.Message('AccessGroupDemoteAdmin', buttons=uiconst.YESNO) != uiconst.ID_YES:
                return True
        elif accessRight == ownergroupConst.MEMBERSHIP_TYPE_MANAGER and newRight not in (ownergroupConst.MEMBERSHIP_TYPE_ADMIN, ownergroupConst.MEMBERSHIP_TYPE_MANAGER):
            if eve.Message('AccessGroupDemoteManager', buttons=uiconst.YESNO) != uiconst.ID_YES:
                return True
        return False

    def RemoveMembers(self, groupID, memberIDs):
        if session.charid in memberIDs:
            if eve.Message('AccessGroupRemoveYourselfFromGroup', buttons=uiconst.YESNO) != uiconst.ID_YES:
                memberIDs.discard(session.charid)
        if not memberIDs:
            return
        failed = self.remoteSvc.DeleteMembers(groupID, list(memberIDs))
        self.DisplayWarningIfNeeded(failedInfo=failed)
        memberIDsToUpdate = GetMemberIDsToUpdate(memberIDs, failed)
        self.RemoveFromMemberCache(groupID, memberIDsToUpdate)
        self.on_groupmembers_removed(groupID, memberIDsToUpdate)

    def GetUpdateMemberDict(self, memberIDs, newMembershipType, failed):
        failedMemberIDs = {x[0] for x in failed}
        membersToUpdate = {x:newMembershipType for x in memberIDs if x not in failedMemberIDs}
        return membersToUpdate

    def SetGroupMembersWithSameRight(self, groupID, memberIDs, membershipType):
        currentMembers = self.GetMembers(groupID)
        oldMemberIDs, newMembersAndMembershipType = self._GetNewAndOldMemberInfo(memberIDs, currentMembers.keys(), membershipType)
        failed = []
        if oldMemberIDs:
            failed += self.UpdateMembershipTypes(groupID, list(oldMemberIDs), membershipType, silently=True)
        if newMembersAndMembershipType:
            failed += self.AddMembers(groupID, newMembersAndMembershipType, silently=True)
        self.DisplayWarningIfNeeded(failedInfo=failed)
        membersToUpdate = self.GetUpdateMemberDict(memberIDs, membershipType, failed)
        if membersToUpdate:
            self.UpdateMemberCache(groupID, membersToUpdate)
            self.on_groupmembers_changed(groupID)

    def _GetNewAndOldMemberInfo(self, memberIDs, currentGroupMemberIDs, membershipType):
        oldMemberIDs = set()
        newMembersAndMembershipType = {}
        for memberID in memberIDs:
            if memberID in currentGroupMemberIDs:
                oldMemberIDs.add(memberID)
            else:
                newMembersAndMembershipType[memberID] = membershipType

        return (oldMemberIDs, newMembersAndMembershipType)

    def DisplayWarningIfNeeded(self, failedInfo):
        if failedInfo:
            warningLabelList = GetTextForWarning(failedInfo)
            textList = []
            for label, kwargs in warningLabelList:
                textForGroup = GetByLabel(label, **kwargs)
                textList.append(textForGroup)

            warningText = '<br><br>'.join(textList)
            if warningText:
                eve.Message('CustomInfo', {'info': warningText}, modal=False)

    def OnOwnerGroupsUpdated(self, changedGroups):
        selectedGroupID = settings.user.ui.Get('accessGroup_lastGroup', None)
        self.myGroupsCacheInvalidated = False
        for groupID, recordedChanges in changedGroups.iteritems():
            self.ProccessGroupChange(groupID, recordedChanges, selectedGroupID)

    def ProccessGroupChange(self, groupID, recordedChanges, selectedGroupID):
        if ownergroupConst.GROUP_DELETED in recordedChanges:
            self.InvalidateGetMyGroupsIfNeeded()
            self.on_group_deleted()
            return
        if self.IsInChange([ownergroupConst.GROUP_NAME_CHANGED, ownergroupConst.GROUP_DESCRIPTION_CHANGED], recordedChanges):
            self.InvalidateGetMyGroupsIfNeeded()
            self.on_group_updated(groupID)
        if self.IsInChange([ownergroupConst.GROUP_MEMBER_ADDED, ownergroupConst.GROUP_MEMBERTYPE_CHANGED, ownergroupConst.GROUP_MEMBER_REMOVED], recordedChanges):
            oldGroupMembers = self.membersByGroupID.get(groupID, {}).copy()
            self.InvalidateGetMemberCache(groupID)
            if ownergroupConst.GROUP_CHANGED_FOR_LISTENER in recordedChanges:
                self.InvalidateGetMyGroupsIfNeeded()
                self.on_group_updated(groupID)
                return
            if selectedGroupID == groupID:
                if ownergroupConst.GROUP_MEMBER_REMOVED in recordedChanges:
                    self.OnCharactersRemoved(groupID, oldGroupMembers)
                self.on_groupmembers_changed(groupID)

    def InvalidateGetMemberCache(self, groupID):
        self.objectCashingSvc.InvalidateCachedMethodCall(REMOTE_SERVICE_NAME, 'GetMembers', groupID)
        self.membersByGroupID.pop(groupID, None)

    def InvalidateGetMyGroupsIfNeeded(self):
        if not self.myGroupsCacheInvalidated:
            self.InvalidateGetMyGroups()
        self.myGroupsCacheInvalidated = True

    def InvalidateGetMyGroups(self):
        self.objectCashingSvc.InvalidateCachedMethodCall(REMOTE_SERVICE_NAME, 'GetMyGroups')
        self.groupByGroupID = None

    def OnCharactersRemoved(self, groupID, oldGroupMembers):
        newMembers = self.GetMembers(groupID)
        removedMemberIDs = {x for x in oldGroupMembers if x not in newMembers}
        if removedMemberIDs:
            self.on_groupmembers_removed(groupID, removedMemberIDs)

    def IsInChange(self, changeList, recordedChanges):
        return bool(set(changeList) & set(recordedChanges))

    def GetCurrentSearchResults(self):
        return self.currentSearchResults

    def SetCurrentSearchResults(self, searchResults):
        self.currentSearchResults = searchResults
        self.on_groups_reload()

    def GetMenuForGroupID(self, node):
        return MenuProvider().GetMenuForGroupID(node, self)

    def GetMenuForMember(self, groupID, nodes):
        myGroupInfo = self.GetMyGroupInfo(groupID)
        corpOwned = self.IsGroupCorpOwned(groupID)
        return MenuProvider().GetMenuForMember(groupID, nodes, myGroupInfo.membershipType, self, corpOwned)
