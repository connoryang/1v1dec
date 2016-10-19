#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\station\medical\__init__.py
from eve.client.script.ui.station.medical.medicalControllers import MedicalControllerStation, MedicalControllerStructure

def GetMedicalController():
    if session.stationid2:
        return MedicalControllerStation()
    if session.structureid:
        return MedicalControllerStructure()
