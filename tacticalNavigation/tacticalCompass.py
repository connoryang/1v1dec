#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\tacticalNavigation\tacticalCompass.py
from evegraphics.wrappers.vectorFunctions import OffsetPositionFunction
import evegraphics.wrappers.vectorFunctions as functions
import geo2
import trinity
import math
import tacticalNavigation.ui as navUI
_LINESET_SMOOTH_PATH = 'res:/ui/inflight/tactical/tacticalLineSet.red'
_DARK_DISK_PATH = 'res:/ui/inflight/tactical/tacticalDarkDisc.red'
_OPTIMAL_GRADIENT_PATH = 'res:/ui/inflight/tactical/tacticalOptimalGradient.red'
_FALLOFF_GRADIENT_PATH = 'res:/ui/inflight/tactical/tacticalFalloffGradient.red'
_RANGE_SPHERE_PATH = 'res:/ui/inflight/tactical/rangeSphere.red'
_RANGES = [5,
 10,
 20,
 30,
 40,
 50,
 75,
 100,
 150,
 200,
 250,
 300,
 400,
 500,
 750,
 1000,
 1500,
 2000]
_MAJOR_RANGES = [50,
 100,
 250,
 500,
 1000]
_COLOR_ATTACK_RANGE = (1.0, 0.1, 0.025)
_COLOR_LABEL = (1.0, 1.0, 1.0, 0.5)
_COLOR_OPTIMAL = _COLOR_ATTACK_RANGE + (0.66,)
_COLOR_FALLOFF = _COLOR_ATTACK_RANGE + (0.33,)
_COLOR_TARGETING_LINE = _COLOR_ATTACK_RANGE + (0.5,)
_COLOR_TARGETING_OVERLAY = _COLOR_ATTACK_RANGE + (1.0,)
_LINE_FADE_IN_START = 2000
_LINE_FADE_IN_END = 5000
_DEFAULT_ACTIVE_RANGE = 200000

class CompassDisc:

    def __init__(self, rootContainer, rangeContainer, discContainer):
        self.lineSet = trinity.Load(_LINESET_SMOOTH_PATH)
        self.rootContainer = rootContainer
        rootContainer.children.append(self.lineSet)
        self.rangeLineSet = trinity.Load(_LINESET_SMOOTH_PATH)
        self.rangeContainer = rangeContainer
        rangeContainer.children.append(self.rangeLineSet)
        self.optimalQuad = trinity.Load(_OPTIMAL_GRADIENT_PATH)
        self.falloffQuad = trinity.Load(_FALLOFF_GRADIENT_PATH)
        self.firingRangeLines = []
        self.rangeLines = []
        self.rangeLabels = {}
        self.rangeLabelsTF = trinity.EveTransform()
        rootContainer.children.append(self.rangeLabelsTF)
        self.arcLines = []
        self.discContainer = discContainer
        self.darkDisc = trinity.Load(_DARK_DISK_PATH)
        self.discContainer.children.append(self.darkDisc)
        self.activeRange = _DEFAULT_ACTIVE_RANGE
        self._activeRangeMeters = 0
        self.targetingRange = 0
        self._baseRadius = 0
        self.targetingRangeLines = []
        self.SetActiveRange(self.activeRange)

    def ClearAll(self):
        for dist in self.rangeLabels:
            for label in self.rangeLabels[dist]:
                label.Destroy()

        self.rangeLabels.clear()
        self.rangeLineSet = None
        del self.rangeLabelsTF.children[:]
        self.rangeLabelsTF = None
        self.optimalQuad = None
        self.falloffQuad = None
        self.rootContainer = None
        self.discContainer = None
        self.darkDisc = None

    def _AddCompassStraightLine(self, angle, range, color):
        x = math.cos(angle)
        y = math.sin(angle)
        xFadeStart = x * self._GetActualDistanceFromMeters(_LINE_FADE_IN_START)
        yFadeStart = y * self._GetActualDistanceFromMeters(_LINE_FADE_IN_START)
        xFadeEnd = x * self._GetActualDistanceFromMeters(_LINE_FADE_IN_END)
        yFadeEnd = y * self._GetActualDistanceFromMeters(_LINE_FADE_IN_END)
        xEnd = x * range
        yEnd = y * range
        lineID = self.lineSet.AddStraightLine((xFadeEnd, 0, yFadeEnd), color, (xEnd, 0, yEnd), color, 1.0)
        self.arcLines.append(lineID)
        c0 = color[:-1] + (0,)
        lineID = self.lineSet.AddStraightLine((xFadeStart, 0, yFadeStart), c0, (xFadeEnd, 0, yFadeEnd), color, 1.0)
        self.arcLines.append(lineID)

    def SetBaseRadius(self, radius):
        if self._baseRadius == radius:
            return
        self._baseRadius = radius
        self._ClearRangeLinesLines()
        self.SetActiveRange(self.activeRange)
        self.SetTargetingRange(self.targetingRange)
        self.HideFiringRange()

    def _GetActualDistanceFromKilometers(self, r):
        return r * 1000.0 + self._baseRadius

    def _GetActualDistanceFromMeters(self, r):
        return r + self._baseRadius

    def _AddDistanceLabel(self, r):
        if r in self.rangeLabels:
            return
        distance = self._GetActualDistanceFromKilometers(r)
        lbl1 = navUI.CreateHoverLabel(str(r), _COLOR_LABEL, None, self.rangeLabelsTF)
        lbl1.SetPosition((distance, 0, 0))
        lbl2 = navUI.CreateHoverLabel(str(r), _COLOR_LABEL, None, self.rangeLabelsTF)
        lbl2.SetPosition((0, 0, -distance))
        lbl3 = navUI.CreateHoverLabel(str(r), _COLOR_LABEL, None, self.rangeLabelsTF)
        lbl3.SetPosition((0, 0, distance))
        lbl4 = navUI.CreateHoverLabel(str(r), _COLOR_LABEL, None, self.rangeLabelsTF)
        lbl4.SetPosition((-distance, 0, 0))
        linstep = min(1.0, max(0.0, (r - 5.0) / 45.0))
        distArg2 = 0.07 - linstep * 0.01
        lbl1.SetDistanceScale2(distArg2)
        lbl2.SetDistanceScale2(distArg2)
        lbl3.SetDistanceScale2(distArg2)
        lbl4.SetDistanceScale2(distArg2)
        self.rangeLabels[r] = (lbl1,
         lbl2,
         lbl3,
         lbl4)

    def _ClearRangeLinesLines(self):
        for lineID in self.rangeLines:
            self.lineSet.RemoveLine(lineID)

        self.rangeLines = []

    def _ClearAndUpdateLabels(self, max_radius_km):
        remove_radii = []
        for label_rad_km in self.rangeLabels:
            if label_rad_km <= max_radius_km:
                continue
            for label in self.rangeLabels[label_rad_km]:
                self.rangeLabelsTF.children.remove(label.extraTransform)

            remove_radii.append(label_rad_km)

        for rad in remove_radii:
            for label in self.rangeLabels[rad]:
                label.Destroy()

            del self.rangeLabels[rad]

        for rad_km in _RANGES:
            if rad_km > max_radius_km:
                break
            if rad_km in self.rangeLabels:
                continue
            self._AddDistanceLabel(rad_km)

        for rad_km in self.rangeLabels:
            distance = self._GetActualDistanceFromKilometers(rad_km)
            self.rangeLabels[rad_km][0].SetPosition((distance, 0, 0))
            self.rangeLabels[rad_km][1].SetPosition((0, 0, -distance))
            self.rangeLabels[rad_km][2].SetPosition((0, 0, distance))
            self.rangeLabels[rad_km][3].SetPosition((-distance, 0, 0))

    def SetActiveRange(self, activeRange):
        real_meters = 0
        max_range_km = 100
        for range_km in _RANGES:
            real_meters = self._GetActualDistanceFromKilometers(range_km)
            max_range_km = range_km
            if real_meters > self._GetActualDistanceFromMeters(activeRange):
                break

        if real_meters == self._activeRangeMeters:
            return
        self._activeRangeMeters = real_meters
        self._ClearAndUpdateLabels(max_range_km)
        self.activeRange = activeRange
        self._ClearRangeLinesLines()
        color_major = (1, 1, 1, 0.33)
        color_minor = (1, 1, 1, 0.125)
        for r in _RANGES:
            if r in _MAJOR_RANGES:
                color = color_major
            else:
                color = color_minor
            actual_radius = self._GetActualDistanceFromKilometers(r)
            if actual_radius > real_meters:
                break
            a = 0.75 * math.pow((real_meters - actual_radius) / real_meters, 0.4) + 0.25
            color = color[:-1] + (color[-1] * a,)
            self.AddCircle(actual_radius, color, self.lineSet, self.rangeLines)

        for lineID in self.arcLines:
            self.lineSet.RemoveLine(lineID)

        self.arcLines = []
        inc = 2.0 * math.pi * 0.25
        inc_s = 0.25 * inc
        colFaint = (1, 1, 1, 0.015)
        colMed = (1, 1, 1, 0.025)
        colStrong = (1, 1, 1, 0.05)
        colNorth = (0.9, 0.6, 0.2, 0.25)
        angle = 0.0
        for i in range(4):
            if i == 1:
                self._AddCompassStraightLine(angle, real_meters, colNorth)
            else:
                self._AddCompassStraightLine(angle, real_meters, colStrong)
            self._AddCompassStraightLine(angle + inc_s, real_meters, colFaint)
            self._AddCompassStraightLine(angle + 2 * inc_s, real_meters, colMed)
            self._AddCompassStraightLine(angle + 3 * inc_s, real_meters, colFaint)
            angle += inc

        self.lineSet.SubmitChanges()
        self.darkDisc.scaling = (real_meters * 2,) * 3
        self.SetTargetingRange(self.targetingRange)

    def AddCircleArc(self, start, end, radius, color, lineSet):
        width = math.sqrt(2 * radius)
        start = geo2.Vec3Scale(start, radius)
        end = geo2.Vec3Scale(end, radius)
        return lineSet.AddSpheredLineCrt(start, color, end, color, (0, 0, 0), width)

    def AddCircle(self, radius, color, lineSet, idSequence = None):
        ids = []
        ids.append(self.AddCircleArc((1, 0, 0), (0, 0, 1), radius, color, lineSet))
        ids.append(self.AddCircleArc((0, 0, 1), (-1, 0, 0), radius, color, lineSet))
        ids.append(self.AddCircleArc((-1, 0, 0), (0, 0, -1), radius, color, lineSet))
        ids.append(self.AddCircleArc((0, 0, -1), (1, 0, 0), radius, color, lineSet))
        if idSequence is not None:
            idSequence.extend(ids)

    def ShowFiringRange(self, optimalRange, falloff, useSurfaceDistance = True):
        self.HideFiringRange()
        optimalActual = optimalRange
        if useSurfaceDistance:
            optimalActual = self._GetActualDistanceFromMeters(optimalRange)
        self.optimalQuad.scaling = (2 * optimalActual, 2 * optimalActual, 2 * optimalActual)
        self.rangeContainer.children.append(self.optimalQuad)
        self.AddCircle(optimalActual, _COLOR_OPTIMAL, self.rangeLineSet, self.firingRangeLines)
        if falloff > optimalRange:
            falloffActual = falloff
            if useSurfaceDistance:
                falloffActual = self._GetActualDistanceFromMeters(falloff)
            self.falloffQuad.scaling = (2 * falloffActual * 1.1, 2 * falloffActual * 1.1, 2 * falloffActual * 1.1)
            self.rangeContainer.children.append(self.falloffQuad)
            self.AddCircle(falloffActual, _COLOR_FALLOFF, self.rangeLineSet, self.firingRangeLines)
        self.rangeLineSet.SubmitChanges()

    def HideFiringRange(self):
        self.rangeContainer.children.fremove(self.optimalQuad)
        self.rangeContainer.children.fremove(self.falloffQuad)
        for lineID in self.firingRangeLines:
            self.rangeLineSet.RemoveLine(lineID)

        self.rangeLineSet.SubmitChanges()
        self.firingRangeLines = []

    def SetTargetingRange(self, targetingRange):
        for lineID in self.targetingRangeLines:
            self.lineSet.RemoveLine(lineID)

        self.targetingRangeLines = []
        self.targetingRange = targetingRange
        if targetingRange > 0:
            actualTargetingRange = self._GetActualDistanceFromMeters(targetingRange)
            self.AddCircle(actualTargetingRange, _COLOR_TARGETING_LINE, self.lineSet, self.targetingRangeLines)
            for lineID in self.targetingRangeLines:
                self.lineSet.ChangeLineAnimation(lineID, _COLOR_TARGETING_OVERLAY, 0.0, 40)

        self.lineSet.SubmitChanges()


class TacticalCompass:

    def __init__(self):
        self.rootPersistenceKey = (self, 'rootTransform')
        self.rootCurve = OffsetPositionFunction(None)
        self.sceneManager = sm.GetService('sceneManager')
        self.rootTransform = trinity.EveRootTransform()
        self.rootTransform.translationCurve = self.rootCurve.GetBlueFunction()
        self.sceneManager.RegisterPersistentSpaceObject(self.rootPersistenceKey, self.rootTransform)
        self.rootTransform.name = 'TacticalOverlayMain'
        self.connectorPersistenceKey = (self, 'connectorContainer')
        self.connectorContainer = trinity.Load('res:/ui/inflight/tactical/tacticalOverlay.red')
        self.connectorContainer.translationCurve = self.rootCurve.GetBlueFunction()
        self.sceneManager.RegisterPersistentSpaceObject(self.connectorPersistenceKey, self.connectorContainer)
        self.anchorDiffuse = self.connectorContainer.anchorEffect.parameters.FindByName('DiffuseColor')
        self.bombSphere = trinity.Load(_RANGE_SPHERE_PATH)
        self.bombSpherePersistanceKey = (self, 'bombSphere')
        self.sceneManager.RegisterPersistentSpaceObject(self.bombSpherePersistanceKey, self.bombSphere)
        self.bombRangeAnchorConnector = None
        self.firingRangePersistenceKey = (self, 'firingRange')
        self.firingRangeRoot = trinity.EveRootTransform()
        self.firingRangeRoot.name = 'TacticalOverlayRangeSphere'
        self.sceneManager.RegisterPersistentSpaceObject(self.firingRangePersistenceKey, self.firingRangeRoot)
        self.darkDiscPersistenceKey = (self, 'darkDisc')
        self.darkDiscContainer = trinity.EveRootTransform()
        self.darkDiscContainer.name = 'TacticalOverlayDarkDisc'
        self.sceneManager.RegisterPersistentSpaceObject(self.darkDiscPersistenceKey, self.darkDiscContainer)
        self.connectors = {}
        self.selection = None
        self.targetingRange = None
        self.optimalRange = None
        self.falloffRange = None
        self.baseRadius = 0.0
        self.compassDisc = CompassDisc(self.rootTransform, self.firingRangeRoot, self.darkDiscContainer)

    def SetRootBall(self, ball):
        self.baseRadius = getattr(ball, 'radius', 0)
        self.rootCurve.SetParentFunction(ball)
        self.connectorContainer.translationCurve = ball
        self.darkDiscContainer.translationCurve = ball
        self.SetBaseRadius(self.baseRadius)

    def SetMoveMode(self, flag, ball):
        self.connectorContainer.translationCurve = ball
        self.darkDiscContainer.translationCurve = ball
        if flag:
            self.anchorDiffuse.value = navUI.ColorCombination(navUI.COLOR_MOVE, 1.0)
        else:
            self.anchorDiffuse.value = (1, 1, 1, 1)

    def SetBaseRadius(self, radius):
        self.baseRadius = radius
        self.compassDisc.SetBaseRadius(radius)
        self.connectorContainer.sourceRadius = radius

    def GetRootFunction(self):
        return self.rootCurve.GetBlueFunction()

    def SetAggressive(self, ballID, isAggressive):
        if ballID in self.connectors:
            self.connectors[ballID].isAggressive = isAggressive

    def AddConnector(self, ball):
        if ball.id in self.connectors:
            return
        trackObject = trinity.EveTacticalOverlayTrackObject()
        trackObject.translationCurve = ball
        trackObject.radius = getattr(ball, 'radius', 0)
        self.connectorContainer.trackObjects.append(trackObject)
        self.connectors[ball.id] = trackObject

    def SetInterest(self, ball):
        if self.connectorContainer is None:
            return
        if ball is None or ball.id not in self.connectors:
            self.connectorContainer.interestObject = None
            return
        self.connectorContainer.interestObject = self.connectors[ball.id]

    def RemoveConnector(self, ballID):
        if ballID in self.connectors:
            trackObject = self.connectors[ballID]
            if self.connectorContainer.interestObject == trackObject:
                self.connectorContainer.interestObject = None
            self.connectorContainer.trackObjects.fremove(trackObject)
            trackObject.translationCurve = None
            del self.connectors[ballID]

    def GetMaxRange(self):
        return self.connectorContainer.activeRange + self.connectorContainer.rangeFadeLength

    def SetTargetingRange(self, range, setInterestRange):
        self.compassDisc.SetTargetingRange(range)
        activeRange = max(150000.0, range * 1.1)
        self.compassDisc.SetActiveRange(activeRange)
        self.connectorContainer.activeRange = activeRange + self.baseRadius
        self.connectorContainer.rangeFadeLength = max(range * 0.25, 50000)
        if setInterestRange:
            self.connectorContainer.interestRange = range

    def SetFiringRange(self, optimal, falloff):
        if optimal > 0:
            self.compassDisc.ShowFiringRange(optimal, falloff + optimal)
            self.connectorContainer.interestRange = max(optimal, falloff + optimal)

    def ClearAll(self):
        self.ClearConnectors()
        self.sceneManager.RemovePersistentSpaceObject(self.rootPersistenceKey)
        self.rootTransform = None
        self.sceneManager.RemovePersistentSpaceObject(self.connectorPersistenceKey)
        self.connectorContainer = None
        self.sceneManager.RemovePersistentSpaceObject(self.firingRangePersistenceKey)
        self.firingRangeRoot = None
        self.sceneManager.RemovePersistentSpaceObject(self.bombSpherePersistanceKey)
        self.bombSphere.translationCurve = None
        self.bombSphere = None
        self.sceneManager.RemovePersistentSpaceObject(self.darkDiscPersistenceKey)
        self.darkDiscContainer = None
        self.rootCurve = None
        self.compassDisc.ClearAll()

    def ClearConnectors(self):
        ids = self.connectors.keys()
        for each in ids:
            self.RemoveConnector(each)

    def ShowCynoRange(self, radius):
        self.HideBombRange()
        self.connectorContainer.interestRange = self.compassDisc.targetingRange
        self.bombSphere.translationCurve = self.rootCurve.GetBlueFunction()
        self.bombSphere.display = True
        scale = 2 * radius
        self.bombSphere.scaling = (scale, scale, scale)
        self.firingRangeRoot.translationCurve = self.rootCurve.GetBlueFunction()
        self.compassDisc.ShowFiringRange(radius, radius, False)

    def ShowBombRange(self, bombRadius, distance, ball):
        self.HideBombRange()
        positionFunction = OffsetPositionFunction(ball, (0, 0, distance + self.baseRadius), ball)
        self.connectorContainer.interestRange = self.compassDisc.targetingRange
        self.bombSphere.translationCurve = positionFunction.GetBlueFunction()
        self.bombSphere.display = True
        scale = 2 * bombRadius
        self.bombSphere.scaling = (scale, scale, scale)
        rootCurve = self.GetRootFunction()
        centerFunction = functions.XZPlaneRotationFunction(self.GetRootFunction(), positionFunction.GetBlueFunction())
        centerFunction = centerFunction.GetBlueFunction()
        self.firingRangeRoot.translationCurve = centerFunction
        self.bombRangeAnchorConnector = navUI.CreateCurvedAnchorConnector(navUI.STYLE_FAINT, navUI.COLOR_ATTACK, rootCurve, positionFunction.GetBlueFunction())
        self.compassDisc.ShowFiringRange(bombRadius, bombRadius, False)

    def HideBombRange(self):
        if self.bombRangeAnchorConnector is not None:
            self.bombRangeAnchorConnector.Destroy()
            self.bombRangeAnchorConnector = None
        self.compassDisc.HideFiringRange()
        self.connectorContainer.interestRange = self.compassDisc.targetingRange
        self.firingRangeRoot.translationCurve = self.GetRootFunction()
        self.bombSphere.translationCurve = None
        self.bombSphere.display = False
