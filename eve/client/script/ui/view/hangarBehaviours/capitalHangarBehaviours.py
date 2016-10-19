#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\view\hangarBehaviours\capitalHangarBehaviours.py
import evetypes
import const
import geo2
import trinity
from baseHangarBehaviours import BaseHangarShipBehaviour, BaseHangarTrafficBehaviour
import eveHangar.hangar as hangarUtil

class CapitalHangarShipBehaviour(BaseHangarShipBehaviour):

    def SetAnchorPoint(self, hangarScene):
        if hangarScene is None:
            self.log.error('CapitalHangarShipBehaviour.SetAnchorPoint: Setting anchor point when scene is None')
            return
        eveStations = hangarScene.Find('trinity.EveStation2')
        for stationObject in eveStations:
            anchorPointLocatorSets = [ locatorSet for locatorSet in getattr(stationObject, 'locatorSets', []) if locatorSet.name == 'anchorpoint' ]
            if len(anchorPointLocatorSets) > 0:
                if len(getattr(anchorPointLocatorSets[0], 'locators', [])) > 0:
                    self.shipAnchorPoint = anchorPointLocatorSets[0].locators[0][0]
                    return

        self.log.warning('CapitalHangarShipBehaviour.SetAnchorPoint: Could not find anchor point')

    def PlaceShip(self, model, typeID):
        model.translationCurve = trinity.TriVectorCurve()
        trinity.WaitForResourceLoads()
        localBB = model.GetLocalBoundingBox()
        width = abs(localBB[0][0])
        if evetypes.GetGroupID(typeID) == const.groupTitan:
            width += 2000
        self.endPos = geo2.Vec3Add(self.shipAnchorPoint, (width, 0.0, 0.0))
        model.translationCurve.value = self.endPos
        self.ApplyShipBobbing(model, (0.0, model.translationCurve.value[1], 0.0), (0.0, 250.0, 0.0), model.GetBoundingSphereRadius())

    def GetAnimEndPosition(self):
        return self.endPos

    def GetAnimStartPosition(self):
        return self.endPos


class CapitalHangarTrafficBehaviour(BaseHangarTrafficBehaviour):

    def __init__(self):
        super(CapitalHangarTrafficBehaviour, self).__init__()
        self.hangarTraffic = hangarUtil.HangarTraffic()

    def Setup(self, scene):
        self.hangarTraffic.SetupScene(scene)

    def CleanUp(self):
        if self.hangarTraffic:
            self.hangarTraffic.CleanupScene()
        self.hangarTraffic = None
