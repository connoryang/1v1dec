#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\fittingStanceButtons.py
from eve.client.script.ui.inflight.shipstance import ShipStanceButtonController

class GhostShipStanceButtonController(ShipStanceButtonController):

    def get_ship_stance(self, ship_id, type_id):
        return sm.GetService('ghostFittingSvc').GetSimulatedShipStance(ship_id, type_id)

    def set_stance(self, stance_id, ship_id):
        return sm.GetService('ghostFittingSvc').SetSimulatedStance(stance_id, ship_id)
