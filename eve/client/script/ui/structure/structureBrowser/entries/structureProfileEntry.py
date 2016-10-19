#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureBrowser\entries\structureProfileEntry.py
import itertoolsext
from carbon.common.script.sys.serviceConst import ROLEMASK_ELEVATEDPLAYER
from carbonui.control.menuLabel import MenuLabel
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.structure import ChangeSignalConnect
from eve.client.script.ui.structure.structureBrowser.nameAndDescriptionWnd import EditProfileNameAndDescriptionWnd
from eve.client.script.ui.structure.structureSettings.profileEntry import ProfileEntryBase
import carbonui.const as uiconst
import blue
import log
import eve.client.script.ui.structure.structureBrowser.browserUIConst as browserUIConst

class StructureProfileEntry(ProfileEntryBase):
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_NORMAL
    ENTRYHEIGHT = 36

    def ApplyAttributes(self, attributes):
        ProfileEntryBase.ApplyAttributes(self, attributes)
        self.sr.node = self.node = attributes.node
        self.profileController = self.node.profileController
        self.allStructuresProfileController = self.node.allStructuresProfileController
        self.structureBrowserController = self.node.structureBrowserController
        self.ChangeSignalConnection(connect=True)
        isSelected = self.node.isSelected
        self.node.isSelected = None
        if isSelected:
            self.Select()
        profileName = self.profileController.GetProfileName()
        self.profileNameLabel = EveLabelMedium(name='profileName', parent=self, left=10, align=uiconst.CENTERLEFT, text=profileName)
        self.hint = self.profileController.GetProfileDescription()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.structureBrowserController.on_profile_selected, self.OnProfileSelected), (self.allStructuresProfileController.on_profile_assigned, self.OnProfileAssigned)]
        ChangeSignalConnect(signalAndCallback, connect)

    def Load(self, node):
        pass

    def OnClick(self, *args):
        if not self.structureBrowserController.HasProfileChanged():
            self.Select()
        profileID = self.profileController.GetProfileID()
        self.structureBrowserController.SelectProfile(profileID)

    def OnDropData(self, dragSource, dragData):
        firstNode = dragData[0]
        isMyCorpStructureEntry = getattr(firstNode, 'isMyCorpStructureEntry', False)
        if not isMyCorpStructureEntry:
            return
        profileID = self.profileController.GetProfileID()
        if profileID == browserUIConst.ALL_PROFILES:
            return
        structureIDs = []
        for eachNode in dragData:
            structureIDs.append(eachNode.itemID)

        self.allStructuresProfileController.UpdateProfileIDForStructures(profileID, structureIDs)

    def IsThisProfile(self, profileID):
        return profileID == self.profileController.GetProfileID()

    def OnProfileSelected(self, profileID):
        if self.destroyed:
            return
        if self.IsThisProfile(profileID):
            self.Select()
        else:
            self.Deselect()

    def OnProfileAssigned(self, profileID):
        if not self.IsThisProfile(profileID):
            return
        self.CheckConstructBlinkBG()
        uicore.animations.FadeTo(self.blinkBG, 0.0, 0.25, duration=0.25, curveType=uiconst.ANIM_WAVE, loops=2)

    def GetMenu(self, *args):
        m = [(MenuLabel('UI/StructureBrowser/EditNameAndDescription'), self.EditNameAndDescription, ()), (MenuLabel('UI/StructureBrowser/DeleteProfile'), self.DeleteProfile, ())]
        if session.role & ROLEMASK_ELEVATEDPLAYER:
            profileID = self.profileController.GetProfileID()
            m.append(('GM: profileID: ' + str(profileID), blue.pyos.SetClipboardData, (str(profileID),)))
        return m

    def DeleteProfile(self, *args):
        profileID = self.profileController.GetProfileID()
        structureControllers = self.structureBrowserController.GetMyStructures()
        usingProfile = itertoolsext.count(structureControllers, lambda x: x.GetProfileID() == profileID)
        if usingProfile:
            raise UserError('CannotDeleteStructureProfileInUse', {'numStructures': usingProfile})
        reply = eve.Message('DeleteStructureProfile', buttons=uiconst.YESNO)
        if reply != uiconst.ID_YES:
            return
        self.allStructuresProfileController.DeleteProfile(profileID)
        self.structureBrowserController.ProfileDeleted(profileID)

    def EditNameAndDescription(self):
        EditProfileNameAndDescriptionWnd(controller=self.profileController)

    def Close(self):
        try:
            self.ChangeSignalConnection(connect=False)
        except Exception as e:
            log.LogError('Failed at closing profile entry, e = ', e)
        finally:
            self.profileController = None
            self.allStructuresProfileController = None
            self.structureBrowserController = None
            ProfileEntryBase.Close(self)


class StructureAllProfilesEntry(StructureProfileEntry):

    def ApplyAttributes(self, attributes):
        StructureProfileEntry.ApplyAttributes(self, attributes)
        self.profileNameLabel.bold = True
        if self.rightBtn:
            self.rightBtn.Close()
            self.rightBtn = None

    def GetMenu(self):
        return []
