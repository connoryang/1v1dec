#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\dockedUI\controllers\structureController.py
import structures
import util
from eve.client.script.ui.shared.dockedUI.controllers.baseController import BaseStationController
from carbon.common.script.sys.serviceConst import ROLE_GML
import invCont

class StructureController(BaseStationController):

    def __init__(self, itemID = None):
        BaseStationController.__init__(self)
        self.structureID = itemID
        self.structureItem = None

    def _GetStructureItem(self):
        if self.structureItem is None:
            inv = sm.GetService('invCache').GetInventoryFromId(self.structureID)
            item = inv.GetItem()
            self.structureItem = item
        return self.structureItem

    def ChangeDockedMode(self, viewState):
        if viewState.HasActiveTransition():
            return
        if sm.GetService('viewState').IsViewActive('structure'):
            sm.GetService('cmd').CmdEnterHangar()
        else:
            sm.GetService('cmd').CmdEnterStructure()

    def Undock(self):
        sm.GetService('structureDocking').Undock(self.structureID)

    def GetServicesInStation(self):
        onlineServices = sm.GetService('structureServices').GetCurrentStructureServices()
        return self._GetServiceInfoAvailable(onlineServices)

    def GetCurrentStateForService(self, serviceID):
        try:
            hasAccessTo = sm.GetService('structureServices').IsServiceAvailable(serviceID)
        except KeyError:
            return util.KeyVal(isEnabled=True)

        return util.KeyVal(isEnabled=hasAccessTo)

    def GetGuests(self):
        return sm.GetService('structureGuests').GetGuests()

    def GetOwnerID(self):
        return self._GetStructureItem().ownerID

    def GetStationItemsAndShipsClasses(self):
        return (invCont.StructureItemHangar, invCont.StructureShipHangar)

    def GetItemID(self):
        return self.structureID

    def GetDockedModeTextPath(self, viewName = None):
        if sm.GetService('viewState').IsViewActive('hangar'):
            return 'UI/Commands/EnterStructure'
        else:
            return 'UI/Commands/EnterHangar'

    def CanTakeControl(self):
        return sm.GetService('structureControl').CanBoard(self.GetItemID())

    def IsHqAllowed(self):
        return False

    def IsControlable(self):
        return True

    def TakeControl(self):
        sm.GetService('structureControl').Board(self.GetItemID())

    def GetCharInControl(self):
        inv = sm.GetService('invCache').GetInventoryFromId(self.GetItemID())
        return inv.GetPilot()

    def GetNumberOfUnrentedOffices(self):
        return None

    def CorpsWithOffices(self):
        return sm.GetService('structureOffices').GetCorporations()

    def RentOffice(self, cost):
        sm.GetService('structureOffices').RentOffice(cost)

    def UnrentOffice(self):
        sm.GetService('structureOffices').UnrentOffice()

    def DoesOfficeExist(self):
        return sm.GetService('structureOffices').HasOffice()

    def GetCostForOpeningOffice(self):
        return sm.GetService('structureOffices').GetCost()
