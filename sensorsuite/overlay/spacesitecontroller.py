#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\sensorsuite\overlay\spacesitecontroller.py
from sensorsuite.error import InvalidClientStateError
import carbonui.const as uiconst
from sensorsuite.overlay.sitestore import SiteMapStore
from sensorsuite.overlay.sitetype import STRUCTURE
from sensorsuite.overlay.spacelocations import SpaceLocations
import sensorsuite.overlay.const as overlayConst
import uthread2

class SpaceSiteController:

    def __init__(self, sensorSuiteService, michelle):
        self.sensorSuiteService = sensorSuiteService
        self.michelle = michelle
        self.siteMaps = SiteMapStore()
        self.spaceLocations = SpaceLocations()
        self.siteHandlers = {}

    def Clear(self):
        self.siteMaps.Clear()
        self.spaceLocations.Clear()

    def GetVisibleSiteTypes(self):
        return [ handler.siteType for handler in self.siteHandlers.itervalues() if handler.IsFilterEnabled() ]

    def GetVisibleSiteMap(self):
        return {siteData.siteID:siteData for siteData in self.siteMaps.IterSitesByKeys(*self.GetVisibleSiteTypes()) if self.GetSiteHandler(siteData.siteType).IsVisible(siteData)}

    def GetVisibleSites(self):
        return [ siteData for siteData in self.siteMaps.IterSitesByKeys(*self.GetVisibleSiteTypes()) if self.GetSiteHandler(siteData.siteType).IsVisible(siteData) ]

    def IsSiteVisible(self, siteData):
        handler = self.GetSiteHandler(siteData.siteType)
        return handler.IsFilterEnabled() and handler.IsVisible(siteData)

    def AddSiteHandler(self, siteType, handler):
        handler.SetSiteController(self)
        self.siteHandlers[siteType] = handler

    def GetSiteHandler(self, siteType):
        if siteType in self.siteHandlers:
            return self.siteHandlers[siteType]

    def UpdateSiteVisibility(self, siteTypesToUpdate = None):
        if not siteTypesToUpdate:
            return
        for location in self.spaceLocations.GetLocations():
            siteData = location.siteData
            if siteData.siteType in siteTypesToUpdate:
                removeResult = False
                if not self.IsSiteVisible(siteData):
                    removeResult = True
                elif not (self.sensorSuiteService.IsOverlayActive() or self.sensorSuiteService.sensorSweepActive):
                    removeResult = True
                if removeResult:
                    self.RemoveResult(siteData)

        for siteData in self.GetVisibleSites():
            if siteData.siteType in siteTypesToUpdate:
                if not self.spaceLocations.ContainsSite(siteData.siteID):
                    self.AddSiteToSpace(siteData)

    def NotifySiteChanged(self, siteData):
        self.sensorSuiteService.SendMessage(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_SITE_CHANGED, siteData)

    def RemoveResult(self, siteData):
        if self.spaceLocations.ContainsSite(siteData.siteID):
            locData = self.spaceLocations.GetBySiteID(siteData.siteID)
            self.spaceLocations.RemoveLocation(siteData.siteID)
            locData.bracket.state = uiconst.UI_DISABLED
            locData.bracket.DoExitAnimation(callback=self._ClearBallAndBracket(locData))
        self.NotifySiteChanged(siteData)

    def _ClearBallAndBracket(self, locData):
        return lambda timeoutSeconds: self._ClearBallAndBracketAfterTimeout(timeoutSeconds, locData.bracket, locData.ballRef())

    def _ClearBallAndBracketAfterTimeout(self, timeoutSeconds, bracket, ball):
        uthread2.StartTasklet(self._ClearBallAndBracketAfterTimeout_Thread, timeoutSeconds, bracket, ball)

    def _ClearBallAndBracketAfterTimeout_Thread(self, timeoutSeconds, bracket, ball):
        uthread2.SleepSim(timeoutSeconds)
        self._CloseBracketAndBall(bracket, ball)

    def _IsBallFake(self, ballID):
        return ballID is None or ballID < 0

    def AddSiteToSpace(self, siteData, animate = True):
        if self.spaceLocations.ContainsSite(siteData.siteID):
            return
        if not self.sensorSuiteService.IsSolarSystemReady():
            return
        if not self.IsSiteVisible(siteData):
            return
        if self.sensorSuiteService.IsOverlayActive() or self.sensorSuiteService.sensorSweepActive:
            bracket = self.MakeSiteLocationMarker(siteData)
            if bracket is None:
                return
            if animate:
                bracket.DoEntryAnimation(enable=True)
        self.NotifySiteChanged(siteData)

    def MakeSiteLocationMarker(self, siteData):
        ballpark = self.michelle.GetBallpark()
        if ballpark is None:
            raise InvalidClientStateError('Ballpark has gone missing')
        if siteData.siteType != STRUCTURE:
            siteBall = ballpark.AddClientSideBall(siteData.position, isGlobal=True)
        else:
            siteBall = self.michelle.GetBall(siteData.siteID)
            if siteBall is None:
                return
        siteData.ballID = siteBall.id
        bracketClass = siteData.GetBracketClass()
        bracket = bracketClass(name=str(siteData.siteID), parent=uicore.layer.sensorSuite, data=siteData)
        tracker = bracket.projectBracket
        tracker.trackBall = siteBall
        tracker.name = str(siteData.siteID)
        self.spaceLocations.AddLocation(siteBall, bracket, siteData)
        if self.sensorSuiteService.IsOverlayActive():
            bracket.state = uiconst.UI_NORMAL
        else:
            bracket.state = uiconst.UI_DISABLED
        return bracket

    def _CloseBracket(self, bracket):
        bracket.Close()

    def _CloseBall(self, ball):
        if ball is not None:
            ballpark = self.michelle.GetBallpark()
            if self._IsBallFake(ball.id) and ball.id in ballpark.balls:
                ballpark.RemoveClientSideBall(ball.id)

    def _CloseBracketAndBall(self, bracket, ball):
        self._CloseBracket(bracket)
        self._CloseBall(ball)

    def ClearFromBallpark(self):
        ballpark = self.michelle.GetBallpark()
        if ballpark is not None:
            for data in self.spaceLocations.IterLocations():
                ball = data.ballRef()
                if ball is not None and self._IsBallFake(ball.id) and ball.id in ballpark.balls:
                    ballpark.RemoveClientSideBall(ball.id)

    def ProcessSiteDataUpdate(self, addedSites, removedSites, siteType, addSiteDataMethod):
        removedSiteData = []
        sitesById = self.siteMaps.GetSiteMapByKey(siteType)
        for siteID in removedSites:
            if siteID in sitesById:
                siteData = sitesById.pop(siteID)
                removedSiteData.append(siteData)
                self.RemoveResult(siteData)

        for siteID, rawSiteData in addedSites.iteritems():
            siteData = addSiteDataMethod(siteID, *rawSiteData)
            self.siteMaps.AddSiteToMap(siteType, siteID, siteData)
            try:
                self.AddSiteToSpace(siteData)
            except InvalidClientStateError:
                continue

        if removedSiteData:
            self.sensorSuiteService.UpdateScanner(removedSiteData)

    def UpdateSitePosition(self, siteData):
        ballpark = self.michelle.GetBallpark()
        if ballpark is not None:
            ballpark.UpdateClientSideBallPosition(siteData.ballID, siteData.position)
            self.sensorSuiteService.SendMessage(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_SITE_MOVED, siteData)
