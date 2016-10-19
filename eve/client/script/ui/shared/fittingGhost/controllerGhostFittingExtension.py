#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\controllerGhostFittingExtension.py
import evetypes

class FittingControllerGhostFittingExtension(object):

    def __init__(self):
        pass

    def GetScenePath(self):
        return 'res:/dx9/scene/fitting/previewAmmo.red'

    def GetDogmaLocation(self):
        return sm.GetService('clientDogmaIM').GetFittingDogmaLocation()

    def GhostFitItem(self, item):
        if item:
            return self.GhostFitItemFromTypeID(item.typeID)

    def GhostFitItemFromTypeID(self, typeID):
        dogmaItem = sm.GetService('ghostFittingSvc').TryFitModuleToOneSlot(typeID, preview=True)
        if dogmaItem:
            dogmaItem.isPreviewItem = True
        return dogmaItem

    def UnFitItem(self, ghostItem):
        if ghostItem:
            ghostFittingSvc = sm.GetService('ghostFittingSvc')
            if evetypes.GetCategoryID(ghostItem.typeID) == const.categoryDrone:
                ghostFittingSvc.UnfitDrone(ghostItem.itemID)
            else:
                ghostFittingSvc.UnfitModule(ghostItem.itemID)
