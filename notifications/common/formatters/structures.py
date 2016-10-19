#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\notifications\common\formatters\structures.py
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter
import evetypes
import blue
SOLAR_SYSTEM_ID = 'solarsystemID'
STRUCTURE_ID = 'structureID'
STRUCURE_SHOW_INFO_DATA = 'structureShowInfoData'
SHOW_INFO = 'showinfo'
CORPID_SCOPE = 1000107
CHARID_SCOPECEO = 3004341
TEST_ALLIANCE_ID = 99000025

class BaseStructureNotificationFormatter(BaseNotificationFormatter):

    def __init__(self, localizationImpl = None):
        BaseNotificationFormatter.__init__(self, subjectLabel=self.subjectLabel, bodyLabel=self.bodyLabel)
        self.localization = self.GetLocalizationImpl(localizationImpl)

    @staticmethod
    def GetBaseData(structureID, structureTypeID, solarSystemID):
        showInfoData = (SHOW_INFO, structureTypeID, structureID)
        data = {STRUCTURE_ID: structureID,
         STRUCURE_SHOW_INFO_DATA: showInfoData,
         SOLAR_SYSTEM_ID: solarSystemID}
        return data

    def Format(self, notification):
        data = notification.data
        self._FormatSubject(data, notification)
        self._FormatBody(data, notification)

    def _FormatSubject(self, data, notification):
        notification.subject = self.localization.GetByLabel(self.subjectLabel, **data)

    def _FormatBody(self, data, notification):
        notification.body = self.localization.GetByLabel(self.bodyLabel, **data)

    @staticmethod
    def GetBaseSampleArgs():
        sampleArgs = (1016094240451L, 35834, 30004797)
        return sampleArgs


class StructureFuelAlert(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjStructureFuelAlert'
    bodyLabel = 'Notifications/Structures/bodyStructureFuelAlert'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID, listOfTypesAndQty):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        data['listOfTypesAndQty'] = listOfTypesAndQty
        return data

    def _FormatBody(self, data, notification):
        listOfTypesAndQty = data['listOfTypesAndQty']
        typesAndQtyText = self._GetTextForTypes(listOfTypesAndQty)
        data['typesAndQtyText'] = typesAndQtyText
        notification.body = self.localization.GetByLabel(self.bodyLabel, **data)

    def _GetTextForTypes(self, listOfTypesAndQty):
        textList = [ self.localization.GetByLabel('Notifications/Structures/QtyAndType', qty=x[0], typeID=x[1]) for x in listOfTypesAndQty ]
        return '<br>'.join(textList)

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += ([(1, 1230), (5000000, 638)],)
        return StructureFuelAlert.MakeData(*sampleArgs)


class StructureAnchoring(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjStructureAnchoring'
    bodyLabel = 'Notifications/Structures/bodyStructureAnchoring'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID, corpID, anchoringTimestamp, vulnerableTime):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        ownerCorpName = cfg.eveowners.Get(corpID).name
        ownerCorpLinkData = (SHOW_INFO, const.typeCorporation, corpID)
        data['ownerCorpName'] = ownerCorpName
        data['ownerCorpLinkData'] = ownerCorpLinkData
        data['timeLeft'] = long(max(0, anchoringTimestamp - blue.os.GetWallclockTime()))
        data['vulnerableTime'] = vulnerableTime
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += (1000107, blue.os.GetWallclockTime() + 5 * const.HOUR, 37 * const.MIN)
        return StructureAnchoring.MakeData(*sampleArgs)


class StructureUnanchoring(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjStructureUnanchoring'
    bodyLabel = 'Notifications/Structures/bodyStructureUnanchoring'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID, corpID, anchoringTimestamp):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        ownerCorpName = cfg.eveowners.Get(corpID).name
        ownerCorpLinkData = (SHOW_INFO, const.typeCorporation, corpID)
        data['ownerCorpName'] = ownerCorpName
        data['ownerCorpLinkData'] = ownerCorpLinkData
        data['timeLeft'] = long(max(0, anchoringTimestamp - blue.os.GetWallclockTime()))
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += (1000107, blue.os.GetWallclockTime() + 5 * const.HOUR)
        return StructureUnanchoring.MakeData(*sampleArgs)


class StructureUnderAttack(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjStructureUnderAttack'
    bodyLabel = 'Notifications/Structures/bodyStructureUnderAttack'
    bodyLabelWithoutAlliance = 'Notifications/Structures/bodyStructureUnderAttackWithoutAlliance'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID, shield, armor, hull, aggressorID, aggressorCorpID, aggressorAllianceID = None):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        aggressorCorpName = cfg.eveowners.Get(aggressorCorpID).name
        ownerCorpLinkData = (SHOW_INFO, const.typeCorporation, aggressorCorpID)
        data['shieldPercentage'] = 100 * shield
        data['armorPercentage'] = 100 * armor
        data['hullPercentage'] = 100 * hull
        data['charID'] = aggressorID
        data['corpName'] = aggressorCorpName
        data['corpLinkData'] = ownerCorpLinkData
        data['allianceID'] = aggressorAllianceID
        if aggressorAllianceID:
            data['allianceName'] = cfg.eveowners.Get(aggressorAllianceID).name
            data['allianceLinkData'] = (SHOW_INFO, const.typeAlliance, aggressorAllianceID)
        return data

    def _FormatBody(self, data, notification):
        if data['allianceID']:
            bodyLabel = self.bodyLabel
        else:
            bodyLabel = self.bodyLabelWithoutAlliance
        notification.body = self.localization.GetByLabel(bodyLabel, **data)

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += (0.3,
         0.4,
         0.5,
         CHARID_SCOPECEO,
         CORPID_SCOPE)
        if variant == 0:
            return StructureUnderAttack.MakeData(*sampleArgs)
        else:
            sampleArgs += (TEST_ALLIANCE_ID,)
            return StructureUnderAttack.MakeData(*sampleArgs)


class StructureOnline(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjStructureOnline'
    bodyLabel = 'Notifications/Structures/bodyStructureOnline'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        return StructureOnline.MakeData(*sampleArgs)


class StructureLostShield(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjStructureLostShield'
    bodyLabel = 'Notifications/Structures/bodyStructureLostShield'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID, reinforcedTimestamp, vulnerableTime):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        data['timeLeft'] = long(reinforcedTimestamp - blue.os.GetWallclockTime())
        data['vulnerableTime'] = vulnerableTime
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += (blue.os.GetWallclockTime() + 5 * const.HOUR + 37 * const.MIN, 3 * const.HOUR + 13 * const.MIN)
        return StructureLostShield.MakeData(*sampleArgs)


class StructureLostArmor(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjStructureLostArmor'
    bodyLabel = 'Notifications/Structures/bodyStructureLostArmor'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID, reinforcedTimestamp, vulnerableTime):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        data['timeLeft'] = long(reinforcedTimestamp - blue.os.GetWallclockTime())
        data['vulnerableTime'] = vulnerableTime
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += (blue.os.GetWallclockTime() + 5 * const.HOUR + 37 * const.MIN, 3 * const.HOUR + 13 * const.MIN)
        return StructureLostArmor.MakeData(*sampleArgs)


class StructureDestroyed(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjStructureDestroyed'
    bodyLabel = 'Notifications/Structures/bodyStructureDestroyed'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID, ownerCorpID):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        ownerCorpLinkData = (SHOW_INFO, const.typeCorporation, ownerCorpID)
        data['ownerCorpName'] = cfg.eveowners.Get(ownerCorpID).name
        data['ownerCorpLinkData'] = ownerCorpLinkData
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += (CORPID_SCOPE,)
        return StructureDestroyed.MakeData(*sampleArgs)


class StructureOwnershipTransferred(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/subjOwnershipTransferred'
    bodyLabel = 'Notifications/bodyOwnershipTransferred'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID, newOwnerCorpID, oldOwnerCorpID, charID):
        data = {'structureName': cfg.evelocations.Get(structureID).name or evetypes.GetName(structureTypeID),
         'structureLinkData': ('showinfo', structureTypeID, structureID),
         'toCorporationName': cfg.eveowners.Get(newOwnerCorpID).ownerName,
         'toCorporationLinkData': ('showinfo', const.typeCorporation, newOwnerCorpID),
         'fromCorporationName': cfg.eveowners.Get(oldOwnerCorpID).ownerName,
         'fromCorporationLinkData': ('showinfo', const.typeCorporation, oldOwnerCorpID),
         'solarSystemName': cfg.evelocations.Get(solarSystemID).name,
         'solarSystemLinkData': ('showinfo', const.typeSolarSystem, solarSystemID),
         'characterName': cfg.eveowners.Get(charID).ownerName,
         'characterLinkData': ('showinfo', cfg.eveowners.Get(charID).typeID, charID)}
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += (CORPID_SCOPE, CHARID_SCOPECEO, CORPID_SCOPE)
        return StructureOwnershipTransferred.MakeData(*sampleArgs)


class StructureItemsMovedToSafety(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjAssetsMovedToSafety'
    bodyLabel = 'Notifications/Structures/bodyAssetsMovedToSafety'
    bodyLabelToStructure = 'Notifications/Structures/bodyAssetsMovedToSafetyToStructure'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID, assetSafetyDuration, iskValue, newStructureID = None, newStructureTypeID = None, newStationID = None):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        data['iskValue'] = iskValue
        data['assetSafetyDuration'] = assetSafetyDuration
        data['newStructureID'] = newStructureID
        data['newStationID'] = newStationID
        if newStructureID:
            data['newStructureShowInfoData'] = (SHOW_INFO, newStructureTypeID, newStructureID)
        return data

    def _FormatBody(self, data, notification):
        if data['newStructureID']:
            bodyLabel = self.bodyLabelToStructure
        else:
            bodyLabel = self.bodyLabel
        notification.body = self.localization.GetByLabel(bodyLabel, **data)

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += (3 * const.DAY + 33 * const.MIN, 123456)
        if variant == 0:
            sampleArgs += (1016094240451L, 35834)
            stationID = None
        else:
            stationID = 60009655
        return StructureItemsMovedToSafety.MakeData(newStationID=stationID, *sampleArgs)


class StructureItemsNeedAttention(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjItemsNeedAttention'
    bodyLabel = 'Notifications/Structures/bodyItemsNeedAttention'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        return StructureItemsNeedAttention.MakeData(*sampleArgs)


class StructureMarketOrdersCancelled(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjMarketOrdersCancelled'
    bodyLabel = 'Notifications/Structures/bodyMarketOrdersCancelled'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        return StructureItemsNeedAttention.MakeData(*sampleArgs)


class StructureCloneDestruction(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/subjCloneJumpImplantDestruction'
    bodyLabel = 'Notifications/bodyCloneJumpImplantDestruction'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID, newOwnerCorpID, oldOwnerCorpID, charID):
        data = {'structureName': cfg.evelocations.Get(structureID).name or evetypes.GetName(structureTypeID),
         'structureLinkData': ('showinfo', structureTypeID, structureID),
         'toCorporationName': cfg.eveowners.Get(newOwnerCorpID).ownerName,
         'toCorporationLinkData': ('showinfo', const.typeCorporation, newOwnerCorpID),
         'fromCorporationName': cfg.eveowners.Get(oldOwnerCorpID).ownerName,
         'fromCorporationLinkData': ('showinfo', const.typeCorporation, oldOwnerCorpID),
         'solarSystemName': cfg.evelocations.Get(solarSystemID).name,
         'solarSystemLinkData': ('showinfo', const.typeSolarSystem, solarSystemID),
         'characterName': cfg.eveowners.Get(charID).ownerName,
         'characterLinkData': ('showinfo', cfg.eveowners.Get(charID).typeID, charID)}
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += (CORPID_SCOPE, CHARID_SCOPECEO, CORPID_SCOPE)
        return StructureOwnershipTransferred.MakeData(*sampleArgs)


class StructureCloneMoved(BaseStructureNotificationFormatter):
    pass


class StructureLostDockingAccess(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjLostDockingAccess'
    bodyLabel = 'Notifications/Structures/bodyLostDockingAccess'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        return StructureLostDockingAccess.MakeData(*sampleArgs)


class StructureOfficeRental(BaseStructureNotificationFormatter):
    pass


class StructureOfficeLeaseExpiration(BaseStructureNotificationFormatter):
    pass


class StructureOfficeRental(BaseStructureNotificationFormatter):
    pass


class StructureServicesOffline(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjStructureServicesOffline'
    bodyLabel = 'Notifications/Structures/bodyStructureServicesOffline'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID, listOfServiceModuleIDs):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        data['listOfServiceModuleIDs'] = listOfServiceModuleIDs
        return data

    def _FormatBody(self, data, notification):
        text = self._GetTextForTypes(data['listOfServiceModuleIDs'])
        data['listOfServices'] = text
        notification.body = self.localization.GetByLabel(self.bodyLabel, **data)

    def _GetTextForTypes(self, listOfServiceModuleIDs):
        textList = [ self.localization.GetByLabel('Notifications/Structures/TypeLabel', typeID=x) for x in listOfServiceModuleIDs ]
        return '<br>'.join(textList)

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += ([35892],)
        return StructureServicesOffline.MakeData(*sampleArgs)


class StructureItemsDelivered(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjItemsDelieveredAtStructure'
    bodyLabel = 'Notifications/Structures/bodyItemsDelieveredAtStructure'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID, charID, listOfTypesAndQty):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        data['listOfTypesAndQty'] = listOfTypesAndQty
        data['charID'] = charID
        return data

    def _FormatBody(self, data, notification):
        listOfTypesAndQty = data['listOfTypesAndQty']
        typesAndQtyText = self._GetTextForTypes(listOfTypesAndQty)
        data['typesAndQtyText'] = typesAndQtyText
        notification.body = self.localization.GetByLabel(self.bodyLabel, **data)

    def _GetTextForTypes(self, listOfTypesAndQty):
        textList = [ self.localization.GetByLabel('Notifications/Structures/QtyAndType', qty=x[0], typeID=x[1]) for x in listOfTypesAndQty ]
        return '<br>'.join(textList)

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += (CHARID_SCOPECEO, [(1, 1230), (5000000, 638)])
        return StructureItemsDelivered.MakeData(*sampleArgs)


class StructureCourierContractDestinationChanged(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjCourierContractDestinationChanged'
    bodyLabel = 'Notifications/Structures/bodyCourierContractDestinationChanged'

    @staticmethod
    def MakeData(newStationID, newStationTypeID, newSolarSystemID, oldSolarSystemID, contractName, contractID):
        data = {}
        data['newStationID'] = newStationID
        data['newLocationData'] = (SHOW_INFO, newStationTypeID, newStationID)
        data['oldSolarSystemID'] = oldSolarSystemID
        data['oldSolarSystemDataLink'] = (SHOW_INFO, const.typeSolarSystem, oldSolarSystemID)
        data['contractData'] = ('contract', newSolarSystemID, contractID)
        data['contractName'] = contractName
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        return StructureCourierContractDestinationChanged.MakeData(60014740, 57, 30002634, 30003147, 'testContract', 235)
