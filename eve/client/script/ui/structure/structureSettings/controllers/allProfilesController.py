#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureSettings\controllers\allProfilesController.py
import eve.client.script.ui.structure.structureBrowser.browserUIConst as browserUIConst
from eve.client.script.ui.structure.structureSettings.controllers.slimProfileController import SlimStructureProfileController
from signals import Signal
REMOTE_PROFILE_SVC = 'structureProfiles'

class AllStructureProfileController(object):

    def __init__(self):
        self.allSlimProfileControllers = {}
        self.on_profile_saved = Signal()
        self.on_profile_assigned = Signal()
        self.profileControllersLoad = False
        self.remoteStructureSvc = sm.RemoteSvc(REMOTE_PROFILE_SVC)

    def GetProfiles(self, force = False, createIfMissing = False):
        if not self.profileControllersLoad or force or createIfMissing:
            self.BuildProfileDict(createDefault=createIfMissing)
        return self.allSlimProfileControllers.copy()

    def GetProfileKeys(self):
        if not self.profileControllersLoad:
            self.BuildProfileDict()
        return self.allSlimProfileControllers.keys()

    def BuildProfileDict(self, onlyAddMissing = False, createDefault = False):
        profileData = self.remoteStructureSvc.GetProfiles(createDefault)
        for eachProfile in profileData:
            if onlyAddMissing and eachProfile.profileID in self.allSlimProfileControllers:
                continue
            self.AddControllerToDict(eachProfile)

        self.profileControllersLoad = True

    def AddControllerToDict(self, eachProfile):
        profileController = SlimStructureProfileController(eachProfile.profileID, profileData=eachProfile)
        self.allSlimProfileControllers[eachProfile.profileID] = profileController
        profileController.on_profile_saved.connect(self.OnProfileSaved)

    def OnProfileSaved(self, profileID):
        self.GetProfiles(force=True)
        self.on_profile_saved(profileID)

    def GetNewProfileController(self, name, desc):
        profileID = self.remoteStructureSvc.CreateProfile(name, desc)
        if profileID not in self.allSlimProfileControllers:
            self.BuildProfileDict(onlyAddMissing=True)
        return self.allSlimProfileControllers.get(profileID, None)

    def GetSlimProfileController(self, profileID):
        return self.allSlimProfileControllers.get(profileID, None)

    def UpdateProfileIDForStructures(self, profileID, structureIDs):
        self.remoteStructureSvc.ChangeProfiles(structureIDs, profileID)

    def DeleteProfile(self, profileID):
        self.remoteStructureSvc.DeleteProfile(profileID)
        self.allSlimProfileControllers.pop(profileID)
