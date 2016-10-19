#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\station\fitting\stanceSlot.py
from carbonui.primitives.container import Container
from eve.client.script.ui.inflight import shipstance
import carbonui.const as uiconst

class StanceSlots(Container):

    def __init__(self, **kw):
        super(StanceSlots, self).__init__(**kw)

    def _GetAngles(self):
        return [ 258 - i * 10 for i in xrange(3) ]

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        typeID = attributes.typeID
        if typeID is None:
            typeID = sm.GetService('invCache').GetInventoryFromId(attributes.shipID).GetItem().typeID
        self.shipstances = []
        for angle in self._GetAngles():
            pos = attributes.angleToPos(angle)
            newPos = (pos[0],
             pos[1],
             32,
             32)
            self.shipstances.append(shipstance.ShipStanceFittingButton(shipID=attributes.shipID, typeID=typeID, parent=self, pos=newPos, align=uiconst.TOPLEFT, controller=self.controller))

    def ShowStances(self, shipID, typeID):
        btnControllerClass = self.controller.GetStanceBtnControllerClass()
        shipStanceButtonsArgs = btnControllerClass().get_ship_stance_buttons_args(typeID, shipID)
        for idx, kwargs in enumerate(shipStanceButtonsArgs):
            stanceButton = self.shipstances[idx]
            stanceButton.SetAsStance(shipID, typeID, kwargs['stanceID'], kwargs['stance'])

    def GetStanceContainers(self):
        return self.shipstances
