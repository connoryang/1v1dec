#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureControllersSvc.py
import service

class StructureControllerSvc(service.Service):
    __guid__ = 'svc.structureControllers'
    __servicename__ = 'structureControllers'
    __displayname__ = 'Structure Controllers Service'

    def Run(self, memStream = None):
        self.accessGroupController = None
        self.allStructuresProfileController = None
        self.structureBrowserController = None

    def GetAccessGroupController(self):
        if self.accessGroupController is None:
            from eve.client.script.ui.structure.accessGroups.accessGroupsController import AccessGroupsController
            self.accessGroupController = AccessGroupsController()
        return self.accessGroupController

    def GetAllStructuresProfileController(self):
        if self.allStructuresProfileController is None:
            from eve.client.script.ui.structure.structureSettings.controllers.allProfilesController import AllStructureProfileController
            allStructuresProfileController = AllStructureProfileController()
            self.allStructuresProfileController = allStructuresProfileController
        return self.allStructuresProfileController

    def GetStructureBrowserController(self):
        if self.structureBrowserController is None:
            from eve.client.script.ui.structure.structureBrowser.controllers.structureBrowserController import StructureBrowserController
            structureBrowserController = StructureBrowserController()
            self.structureBrowserController = structureBrowserController
        return self.structureBrowserController

    def GetValidProfileIDs(self):
        allStructuresProfileController = self.GetAllStructuresProfileController()
        return allStructuresProfileController.GetProfileKeys()
