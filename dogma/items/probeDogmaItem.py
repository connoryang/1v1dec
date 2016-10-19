#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\items\probeDogmaItem.py
from baseDogmaItem import BaseDogmaItem
from eve.common.script.sys.idCheckers import IsSolarSystem

class ProbeDogmaItem(BaseDogmaItem):

    def IsOwnerModifiable(self, locationID = None):
        if boot.role == 'client':
            return True
        if not locationID:
            locationID = self.locationID
        if IsSolarSystem(locationID):
            return True
        return False
