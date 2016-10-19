#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\eveHangar\hangar.py
import geo2
import blue
import trinity
import uthread
import random
import math
import logging
log = logging.getLogger(__name__)
racialHangarScenes = {1: 20271,
 2: 20272,
 4: 20273,
 8: 20274}
SHIP_FLOATING_HEIGHT = 360.0
SHIP_CLASS_TRAVEL_DURATION = {'bc': (20.0, 30.0),
 'b': (40.0, 50.0),
 'ca': (60.0, 70.0),
 'c': (15.0, 20.0),
 'dn': (70.0, 90.0),
 'faux': (90.0, 110.0),
 'f': (10.0, 15.0)}

def GetShipTravelDurationFromShipName(shipName):
    modifiedShipName = shipName.split('_')[0]
    modifiedShipName = modifiedShipName[1:]
    modifiedShipName = ''.join([ i for i in modifiedShipName if not i.isdigit() ])
    modifiedShipName = modifiedShipName.lower()
    if modifiedShipName not in SHIP_CLASS_TRAVEL_DURATION:
        log.warn("Got an invalid shipClass for hangar traffic, got '%s' for ship '%s' was expecting one of the following [%s]" % (modifiedShipName, shipName, ', '.join(SHIP_CLASS_TRAVEL_DURATION.keys())))
        modifiedShipName = 'c'
    return SHIP_CLASS_TRAVEL_DURATION[modifiedShipName]


class HangarTraffic:

    def __init__(self):
        self.threadList = []

    def AnimateTraffic(self, ship, area):
        initialAdvance = random.random()
        while True:
            minDuration, maxDuration = GetShipTravelDurationFromShipName(ship.name)
            duration = random.uniform(minDuration, maxDuration)
            if ship.translationCurve and ship.rotationCurve and len(ship.translationCurve.keys) == 2:
                now = blue.os.GetSimTime()
                s01 = random.random()
                t01 = random.random()
                if ship.rotationCurve.value[1] < 0.0:
                    startPos = geo2.Vec3BaryCentric(area['Traffic_Start_1'], area['Traffic_Start_2'], area['Traffic_Start_3'], s01, t01)
                    endPos = geo2.Vec3BaryCentric(area['Traffic_End_1'], area['Traffic_End_2'], area['Traffic_End_3'], s01, t01)
                else:
                    startPos = geo2.Vec3BaryCentric(area['Traffic_End_1'], area['Traffic_End_2'], area['Traffic_End_3'], s01, t01)
                    endPos = geo2.Vec3BaryCentric(area['Traffic_Start_1'], area['Traffic_Start_2'], area['Traffic_Start_3'], s01, t01)
                startPos = geo2.Vec3Add(startPos, geo2.Vec3Scale(geo2.Vec3Subtract(endPos, startPos), initialAdvance))
                startKey = ship.translationCurve.keys[0]
                endKey = ship.translationCurve.keys[1]
                startKey.value = startPos
                startKey.time = 0.0
                startKey.interpolation = trinity.TRIINT_LINEAR
                endKey.value = endPos
                endKey.time = duration
                endKey.interpolation = trinity.TRIINT_LINEAR
                ship.translationCurve.extrapolation = trinity.TRIEXT_CONSTANT
                ship.translationCurve.Sort()
                ship.translationCurve.start = now
                ship.display = True
            delay = random.uniform(5.0, 15.0)
            initialAdvance = 0.0
            blue.pyos.synchro.SleepWallclock(1000.0 * (duration + delay))

    def SetupScene(self, hangarScene):
        for obj in hangarScene.objects:
            if hasattr(obj, 'PlayAnimationEx'):
                obj.PlayAnimationEx('NormalLoop', 0, 0.0, 1.0)

        for obj in hangarScene.objects:
            if '_Traffic_' in obj.name:
                obj.RebuildBoosterSet()

        trafficStartEndArea = {}
        for obj in hangarScene.objects:
            if obj.__bluetype__ == 'trinity.EveStation2':
                for loc in obj.locators:
                    if 'Traffic_Start_' in loc.name or 'Traffic_End_' in loc.name:
                        trafficStartEndArea[loc.name] = geo2.Vec3Transform((0.0, 0.0, 0.0), loc.transform)

        if len(trafficStartEndArea) == 6:
            for obj in hangarScene.objects:
                if '_Traffic_' in obj.name:
                    obj.display = False
                    obj.translationCurve = trinity.TriVectorCurve()
                    obj.translationCurve.keys.append(trinity.TriVectorKey())
                    obj.translationCurve.keys.append(trinity.TriVectorKey())
                    obj.rotationCurve = trinity.TriRotationCurve()
                    if random.randint(0, 1) == 0:
                        obj.rotationCurve.value = geo2.QuaternionRotationSetYawPitchRoll(0.5 * math.pi, 0.0, 0.0)
                    else:
                        obj.rotationCurve.value = geo2.QuaternionRotationSetYawPitchRoll(-0.5 * math.pi, 0.0, 0.0)
                    uthreadObj = uthread.new(self.AnimateTraffic, obj, trafficStartEndArea)
                    uthreadObj.context = 'HangarTraffic::SetupScene'
                    self.threadList.append(uthreadObj)

    def RemoveAudio(self, hangarScene):
        objectsToDelete = []
        for obj in hangarScene.objects:
            if obj.name.startswith('invisible_sound_locator'):
                objectsToDelete.append(obj)

        for objToDelete in objectsToDelete:
            hangarScene.objects.remove(objToDelete)

    def CleanupScene(self):
        for uthreadObj in self.threadList:
            uthreadObj.kill()

        self.threadList = []
