#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureBrowser\nameAndDescriptionWnd.py
from eve.client.script.ui.structure.nameAndDescriptionBaseWnd import NameAndDescBaseWnd
from eve.client.script.ui.structure.structureSettings.controllers.structureProfileController import StructureProfileController
from localization import GetByLabel

class CreateProfileWnd(NameAndDescBaseWnd):
    default_captionLabelPath = 'UI/StructureProfiles/CreateProfile'
    confirmLabelPath = 'UI/StructureProfiles/CreateProfileBtn'
    nameLabelPath = 'UI/StructureProfiles/ProfileName'
    descriptionLabelPath = 'UI/StructureProfiles/ProfileDescription'

    def Confirm(self, name, desc):
        slimProfileController = self.controller.GetNewProfileController(name, desc)
        profileID = slimProfileController.GetProfileID()
        windowID = 'structureProfiler_%s' % profileID
        fullProfileController = StructureProfileController(profileID, nameAndDecInfo=slimProfileController.GetNameAndDescriptionInfo())
        profileID = fullProfileController.GetProfileID()
        self.controller.OnProfileSaved(profileID)
        browserController = sm.GetService('structureControllers').GetStructureBrowserController()
        browserController.SelectProfile(profileID)


class EditProfileNameAndDescriptionWnd(NameAndDescBaseWnd):
    default_captionLabelPath = 'UI/StructureProfiles/EditProfileName'
    confirmLabelPath = 'UI/StructureProfiles/EditProfileNameBtn'
    nameLabelPath = 'UI/StructureProfiles/ProfileName'
    descriptionLabelPath = 'UI/StructureProfiles/ProfileDescription'

    def ApplyAttributes(self, attributes):
        NameAndDescBaseWnd.ApplyAttributes(self, attributes)

    def PostApplyAttributes(self, attributes):
        NameAndDescBaseWnd.PostApplyAttributes(self, attributes)
        oldName = self.controller.GetProfileName()
        caption = GetByLabel(self.default_captionLabelPath, oldGroupName=oldName)
        self.SetCaption(caption)

    def PopulateFields(self):
        oldName = self.controller.GetProfileName()
        self.groupNameField.SetText(oldName)
        oldDesc = self.controller.GetProfileDescription()
        self.groupDescField.SetText(oldDesc)

    def Confirm(self, newName, newDesc):
        profileID = self.controller.GetProfileID()
        self.controller.UpdateProfile(profileID, newName, newDesc)
