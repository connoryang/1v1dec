#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\station\stationServiceConst.py
from eve.common.lib import appConst
from localization import GetByLabel
from utillib import KeyVal
import structures
serviceIDAlwaysPresent = -1
serviceData = (KeyVal(name='charcustomization', command='OpenCharacterCustomization', label=GetByLabel('UI/Station/CharacterRecustomization'), iconID='res:/UI/Texture/WindowIcons/charcustomization.png', serviceID=serviceIDAlwaysPresent, maskServiceIDs=(serviceIDAlwaysPresent,)),
 KeyVal(name='medical', command='OpenMedical', label=GetByLabel('UI/Medical/Medical'), iconID='res:/ui/Texture/WindowIcons/cloneBay.png', serviceID=structures.SERVICE_MEDICAL, maskServiceIDs=(appConst.stationServiceCloning, appConst.stationServiceSurgery, appConst.stationServiceDNATherapy)),
 KeyVal(name='repairshop', command='OpenRepairshop', label=GetByLabel('UI/Station/Repairshop'), iconID='res:/ui/Texture/WindowIcons/repairshop.png', serviceID=structures.SERVICE_REPAIR, maskServiceIDs=(appConst.stationServiceRepairFacilities,)),
 KeyVal(name='reprocessingPlant', command='OpenReprocessingPlant', label=GetByLabel('UI/Station/ReprocessingPlant'), iconID='res:/UI/Texture/WindowIcons/Reprocess.png', serviceID=structures.SERVICE_REPROCESSING, maskServiceIDs=(appConst.stationServiceReprocessingPlant,)),
 KeyVal(name='market', command='OpenMarket', label=GetByLabel('UI/Station/Market'), iconID='res:/ui/Texture/WindowIcons/market.png', serviceID=structures.SERVICE_MARKET, maskServiceIDs=(appConst.stationServiceMarket,)),
 KeyVal(name='fitting', command='OpenFitting', label=GetByLabel('UI/Station/Fitting'), iconID='res:/ui/Texture/WindowIcons/fitting.png', serviceID=structures.SERVICE_FITTING, maskServiceIDs=(appConst.stationServiceFitting,)),
 KeyVal(name='industry', command='OpenIndustry', label=GetByLabel('UI/Industry/Industry'), iconID='res:/UI/Texture/WindowIcons/Industry.png', serviceID=structures.SERVICE_MANUFACTURING_SHIP, maskServiceIDs=(appConst.stationServiceFactory, appConst.stationServiceLaboratory)),
 KeyVal(name='bountyoffice', command='OpenBountyOffice', label=GetByLabel('UI/Station/BountyOffice/BountyOffice'), iconID='res:/ui/Texture/WindowIcons/bountyoffice.png', serviceID=serviceIDAlwaysPresent, maskServiceIDs=(serviceIDAlwaysPresent,)),
 KeyVal(name='navyoffices', command='OpenMilitia', label=GetByLabel('UI/Station/MilitiaOffice'), iconID='res:/ui/Texture/WindowIcons/factionalwarfare.png', serviceID=structures.SERVICE_FACTION_WARFARE, maskServiceIDs=(appConst.stationServiceNavyOffices,)),
 KeyVal(name='insurance', command='OpenInsurance', label=GetByLabel('UI/Station/Insurance'), iconID='res:/ui/Texture/WindowIcons/insurance.png', serviceID=structures.SERVICE_INSURANCE, maskServiceIDs=(appConst.stationServiceInsurance,)),
 KeyVal(name='lpstore', command='OpenLpstore', label=GetByLabel('UI/Station/LPStore'), iconID='res:/ui/Texture/WindowIcons/lpstore.png', serviceID=structures.SERVICE_LOYALTY_STORE, maskServiceIDs=(appConst.stationServiceLoyaltyPointStore,)),
 KeyVal(name='securityoffice', command='OpenSecurityOffice', label=GetByLabel('UI/Station/SecurityOffice'), iconID='res:/UI/Texture/WindowIcons/concord.png', serviceID=structures.SERVICE_SECURITY_OFFICE, maskServiceIDs=(appConst.stationServiceSecurityOffice,)))
serviceDataByNameID = {data.name:data for data in serviceData}
serviceDataByServiceID = {data.serviceID:data for data in serviceData}
serviceIdByMaskId = {x:data.serviceID for data in serviceData for x in data.maskServiceIDs}
