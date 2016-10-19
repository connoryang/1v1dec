#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureBrowser\tempUtils.py
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.ui.station import stationServiceConst
import eve.client.script.ui.structure.structureBrowser.browserUIConst as browserUIConst

def GetStuctureServices(structureServices):
    if structureServices is None:
        return []
    sortServices = set()
    for eachServiceID, eachServiceValue in structureServices.iteritems():
        serviceInfo = stationServiceConst.serviceDataByServiceID.get(eachServiceID, None)
        if serviceInfo is None:
            continue
        sortServices.add((serviceInfo.label, serviceInfo))

    if sortServices:
        sortServices = SortListOfTuples(sortServices)
    return sortServices


def GetGroupingForStructure(typeID):
    return browserUIConst.CITADEL_GROUPING_BY_TYPEID.get(typeID, None)
