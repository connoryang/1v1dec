#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureSettings\controllers\slimProfileController.py
from eve.client.script.ui.structure.structureSettings.controllers.structureProfileController import StructureProfileController
from eve.client.script.ui.structure.structureSettings.structureSettingsWnd import StructureProfileSettingCont
from signals import Signal
REMOTE_PROFILE_SVC = 'structureProfiles'

class SlimStructureProfileController(object):

    def __init__(self, profileID = None, profileData = None):
        self.profileID = profileID
        self.nameAndDecInfo = profileData
        self.on_profile_saved = Signal()

    def GetProfileID(self):
        return self.profileID

    def GetProfileName(self):
        if self.nameAndDecInfo:
            return self.nameAndDecInfo.name
        return ''

    def GetProfileDescription(self):
        if self.nameAndDecInfo:
            return self.nameAndDecInfo.description
        return ''

    def GetNameAndDescriptionInfo(self):
        return self.nameAndDecInfo

    def GetFullProfileController(self):
        profileData = sm.RemoteSvc(REMOTE_PROFILE_SVC).GetProfileSettings(self.profileID)
        fullProfileController = StructureProfileController(self.profileID, profileData=profileData, nameAndDecInfo=self.nameAndDecInfo)
        fullProfileController.on_profile_saved.connect(self.OnProfileSaved)
        return fullProfileController

    def OnProfileSaved(self, profileID):
        self.on_profile_saved(profileID)

    def UpdateProfile(self, profileID, name, description):
        if self.GetProfileDescription() != description or self.GetProfileName() != name:
            sm.RemoteSvc(REMOTE_PROFILE_SVC).UpdateProfile(profileID, name, description)
        self.on_profile_saved(profileID)


class SlimStructureAllProfilesController(SlimStructureProfileController):

    def GetFullProfileController(self):
        fullProfileController = StructureProfileController(self.profileID, nameAndDecInfo=self.nameAndDecInfo)
        return fullProfileController
