#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\accessGroups\searchCont.py
import math
from carbonui.primitives.container import Container
from carbonui.primitives.transform import Transform
from eve.client.script.ui.control.buttons import ButtonIcon
from eve.client.script.ui.control.eveSinglelineEdit import SinglelineEdit
import carbonui.const as uiconst
from localization import GetByLabel
EXPANDED_SEARCH_WIDTH = 200

class SearchCont(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        searchWidth, rotation = self.GetWidthAndRotation()
        texturePath = 'res:/UI/Texture/WindowIcons/peopleandplaces.png'
        searchIconHint = GetByLabel('UI/Structures/AccessGroups/SearchButtonHint')
        self.searchIcon = ButtonIcon(name='searchIcon', parent=self, align=uiconst.CENTERRIGHT, pos=(2, 0, 24, 24), iconSize=24, texturePath=texturePath, func=self.OnSearchBtnClicked, hint=searchIconHint)
        arrowTexturePath = 'res:/UI/Texture/Icons/1_16_99.png'
        self.arrowCont = Transform(name='arrowCont', parent=self, pos=(24, 0, 16, 16), align=uiconst.CENTERRIGHT, rotation=rotation)
        self.expandArrow = ButtonIcon(name='expandArrow', parent=self.arrowCont, pos=(0, 0, 16, 16), iconSize=16, texturePath=arrowTexturePath, func=self.OnExpanderClicked)
        hintText = GetByLabel('UI/Structures/AccessGroups/SearchFieldHint')
        self.searchField = SinglelineEdit(parent=self, align=uiconst.CENTERRIGHT, pos=(40,
         0,
         searchWidth,
         0), OnReturn=self.DoSearch, hinttext=hintText, isCharCorpOrAllianceField=True)
        self.searchField.OnClearButtonClick = self.OnClearingSearchField
        self.searchField.ShowClearButton(hint=GetByLabel('UI/Inventory/Clear'))
        self.memberNamesByMemberID = {}
        self.height = max(self.searchField.height, self.searchIcon.height)
        self.width = self.searchField.left + EXPANDED_SEARCH_WIDTH + 10

    def OnSearchBtnClicked(self, *args):
        if settings.user.ui.Get('accessGroup_searchExpanded', False):
            self.DoSearch()
        else:
            self.OnExpanderClicked()

    def OnExpanderClicked(self, *args):
        isExpandedNow = settings.user.ui.Get('accessGroup_searchExpanded', False)
        settings.user.ui.Set('accessGroup_searchExpanded', not isExpandedNow)
        newWidth, newRotation = self.GetWidthAndRotation()
        uicore.animations.MorphScalar(self.arrowCont, 'rotation', self.arrowCont.rotation, newRotation, duration=0.35)
        uicore.animations.MorphScalar(self.searchField, 'width', startVal=self.searchField.width, endVal=newWidth, duration=0.35)
        if not isExpandedNow:
            self.PrimeMembers()

    def GetWidthAndRotation(self):
        if settings.user.ui.Get('accessGroup_searchExpanded', False):
            return (EXPANDED_SEARCH_WIDTH, math.pi)
        return (0, 0)

    def DoSearch(self, *args):
        searchString = self.searchField.GetValue().lower()
        if len(searchString) < 3:
            self.controller.SetCurrentSearchResults(None)
            return
        allMemberInfo = self.PrimeMembers()
        groupsWithMatchedMembers = set()
        matchedMembers = set()
        for groupID, membersDict in allMemberInfo.iteritems():
            for eachMemberID in membersDict.iterkeys():
                memberName = self.GetMemberName(eachMemberID)
                if memberName.find(searchString) > -1:
                    groupsWithMatchedMembers.add(groupID)
                    matchedMembers.add(eachMemberID)

        searchResults = (matchedMembers, groupsWithMatchedMembers)
        self.controller.SetCurrentSearchResults(searchResults)

    def PrimeMembers(self):
        allMemberInfo, allMemberIDs = self.controller.GetAllMyMemberIDs()
        cfg.eveowners.Prime(allMemberIDs)
        return allMemberInfo

    def GetMemberName(self, memberID):
        memberName = self.memberNamesByMemberID.get(memberID)
        if memberName:
            return memberName
        memberName = cfg.eveowners.Get(memberID).name.lower()
        self.memberNamesByMemberID[memberID] = memberName
        return memberName

    def OnClearingSearchField(self):
        SinglelineEdit.OnClearButtonClick(self.searchField)
        self.DoSearch()
