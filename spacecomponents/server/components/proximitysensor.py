#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\proximitysensor.py
from ballpark.messenger.const import MESSAGE_ON_PROXIMITY
from ccpProfile import TimedFunction
from spacecomponents.common.components.component import Component
from spacecomponents.server.messages import MSG_ON_ADDED_TO_SPACE
import logging
logger = logging.getLogger(__name__)

class ProximitySensor(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        super(ProximitySensor, self).__init__(itemID, typeID, attributes, componentRegistry)
        self.SubscribeToMessage(MSG_ON_ADDED_TO_SPACE, self.OnAddedToSpace)
        self.sensorBallID = None
        self.detectionRange = self.attributes.detectionRange
        logger.debug('created proximity sensor %s', self.itemID)

    def OnAddedToSpace(self, ballpark, _):
        logger.debug('proximity sensor %s added to space', self.itemID)
        self.RegisterSensor(ballpark)

    def RegisterSensor(self, ballpark):
        self.SetBallpark(ballpark)
        self.sensorBallID = ballpark.proximityRegistry.RegisterForProximity(self.itemID, self.detectionRange, self.OnProximity)
        logger.debug('proximity sensor %s registered sensor %s', self.itemID, self.sensorBallID)

    def OnProximity(self, ballId, isEntering):
        self.ballpark.eventMessenger.SendMessage(self.itemID, MESSAGE_ON_PROXIMITY, ballId, isEntering)

    @TimedFunction('ProximitySensor::GetBallIdsInRange')
    def GetBallIdsInRange(self):
        ballIds = []
        for ballId in self.ballpark.GetBallIdsInRange(self.sensorBallID, self.detectionRange):
            if ballId <= 0:
                continue
            ballIds.append(ballId)

        return ballIds

    def GetBubbleId(self):
        return self.ballpark.GetBall(self.sensorBallID).newBubbleId

    def SetBallpark(self, ballpark):
        self.ballpark = ballpark

    def GetSensorBallID(self):
        return self.sensorBallID

    def ReplaceSensor(self, detectionRange = None):
        self._SetDetectionRange(detectionRange)
        if self.sensorBallID is not None:
            self.ballpark.proximityRegistry.RemoveSensorFromItem(self.itemID, self.sensorBallID)
        logger.debug('proximity sensor %s replacing sensor ball %s', self.itemID, self.sensorBallID)
        self.RegisterSensor(self.ballpark)

    def _SetDetectionRange(self, detectionRange):
        if detectionRange and detectionRange > self.detectionRange:
            logger.debug('proximity sensor %s extending detection range from %s to %s', self.itemID, self.detectionRange, detectionRange)
            self.detectionRange = detectionRange

    def GetDistanceTo(self, itemID):
        return self.ballpark.DistanceBetween(self.sensorBallID, itemID)
