#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\parklife\tacticalOverlay.py
import blue
import states as stateConst
import uthread2
import tacticalNavigation.tacticalCompass as tacticalCompass
import tacticalNavigation.ui as tacticalUI
import tacticalNavigation.ballparkFunctions as ballpark

class TacticalOverlay:
    _interestStates = [stateConst.targeting,
     stateConst.targeted,
     stateConst.mouseOver,
     stateConst.selected,
     stateConst.lookingAt]
    _aggressorStates = [stateConst.targeted,
     stateConst.threatTargetsMe,
     stateConst.threatAttackingMe,
     stateConst.flagOutlaw,
     stateConst.flagDangerous,
     stateConst.flagAtWarCanFight,
     stateConst.flagStandingBad,
     stateConst.flagStandingHorrible,
     stateConst.flagAtWarMilitia,
     stateConst.flagAlliesAtWar,
     stateConst.flagSuspect,
     stateConst.flagCriminal,
     stateConst.flagHasKillRight,
     stateConst.flagLimitedEngagement,
     stateConst.targeting]
    _friendlyStates = [stateConst.flagSameFleet, stateConst.flagSameCorp, stateConst.flagSameAlliance]

    def __init__(self, tactical, actionDisplay):
        self.tactical = tactical
        self.actionDisplay = actionDisplay
        self.tacticalCompass = None
        self.initialized = False
        self.showingModuleRange = False
        self.selectedID = None
        self.selectedConnector = None
        self.rootPosition = None
        self.navBalls = []
        self._ballInterests = {}
        self._ballFriendly = {}
        self._ballAggressive = {}

    def Initialize(self):
        if self.initialized:
            return
        self.tacticalCompass = tacticalCompass.TacticalCompass()
        self.initialized = True
        self.InitConnectors()
        self.UpdateTargetingRange()
        self.OnShipChange()
        self.actionDisplay.EnableActionDisplay(True)

    def IsInitialized(self):
        return self.initialized

    def EnableMoveMode(self, curve):
        curveID = getattr(curve, 'id', None)
        if not self.initialized:
            return
        self.tacticalCompass.SetMoveMode(True, curve)
        if curveID == session.shipid or curve is None:
            return
        ego = ballpark.GetBall(session.shipid)
        if ego is not None:
            self.tacticalCompass.AddConnector(ego)

    def DisableMoveMode(self):
        if not self.initialized:
            return
        ego = ballpark.GetBall(session.shipid)
        self.RemoveConnector(session.shipid)
        self.tacticalCompass.SetMoveMode(False, ego)

    def RegisterNavBall(self, ball):
        if ball not in self.navBalls:
            self.navBalls.append(ball)
            self.tacticalCompass.AddConnector(ball)

    def UnregisterNavBall(self, ball):
        if ball in self.navBalls:
            self.navBalls.remove(ball)
            self.RemoveConnector(ball.id)

    def TearDown(self):
        if self.initialized:
            self._ClearSelection()
            self.tacticalCompass.ClearAll()
        self.initialized = False
        self.tacticalCompass = None
        self.actionDisplay.EnableActionDisplay(False)

    def AddConnector(self, ball):
        if self.initialized:
            self.tacticalCompass.AddConnector(ball)
            self._CheckAggressionStates(ball)

    def RemoveConnector(self, ballID):
        if not self.initialized:
            return
        self.tacticalCompass.RemoveConnector(ballID)
        if ballID == self.selectedID:
            self._ClearSelection()
        self._ClearInterest(ballID)

    def _UpdateInterest(self, ballID, state, flag):
        if ballID not in self._ballInterests:
            if flag:
                self._ballInterests[ballID] = set([state])
            return
        if not flag and state in self._ballInterests[ballID]:
            self._ballInterests[ballID].remove(state)
        if flag and state not in self._ballInterests[ballID]:
            self._ballInterests[ballID].add(state)

    def _ClearInterest(self, ballID):
        if ballID in self._ballInterests:
            del self._ballInterests[ballID]
        if ballID in self._ballAggressive:
            del self._ballAggressive[ballID]

    def _IsInteresting(self, ballID):
        return ballID in self._ballInterests and len(self._ballInterests[ballID]) > 0

    def _CheckInterest(self, ballID, state, flag):
        if state not in self._interestStates:
            return
        if self.tacticalCompass is None:
            return
        self._UpdateInterest(ballID, state, flag)
        if self._IsInteresting(ballID):
            ball = ballpark.GetBall(ballID)
            if ball is None:
                return
            self.tacticalCompass.AddConnector(ball)
        else:
            self._ClearInterest(ballID)
            bp = ballpark.GetBallpark()
            if bp is None:
                return
            slimItem = bp.GetInvItem(ballID)
            filtered = self.tactical.GetFilteredStatesFunctionNames()
            alwaysShown = self.tactical.GetAlwaysShownStatesFunctionNames()
            if not self.tactical.WantIt(slimItem, filtered, alwaysShown):
                self.RemoveConnector(ballID)

    def CheckState(self, ballID, state, flag):
        if not self.initialized or ballID == session.shipid:
            return
        if state == stateConst.selected and flag:
            self._ShowDirectionTo(ballID)
        self._CheckInterest(ballID, state, flag)
        self._CheckAggression(ballID, state, flag)

    def _CheckAggressionStates(self, ball):
        checkStates = self._GetMatchingStates(ball.id, self._aggressorStates)
        for state in checkStates:
            self._CheckAggression(ball.id, state, True)

    def _CheckAggression(self, ballID, state, flag):
        if state not in self._aggressorStates:
            return
        aggressionStates = self._ballAggressive.get(ballID, [])
        if flag:
            if state not in aggressionStates:
                aggressionStates.append(state)
        elif state in aggressionStates:
            aggressionStates.remove(state)
        self.tacticalCompass.SetAggressive(ballID, len(aggressionStates) > 0)
        self._ballAggressive[ballID] = aggressionStates

    def _GetMatchingStates(self, itemID, states):
        active = sm.GetService('state').GetStates(itemID, states)
        return [ x[1] for x in zip(active, states) if x[0] ]

    def InitConnectors(self):
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark is None:
            return
        self.tacticalCompass.ClearConnectors()
        filtered = self.tactical.GetFilteredStatesFunctionNames()
        alwaysShown = self.tactical.GetAlwaysShownStatesFunctionNames()
        for itemID, ball in ballpark.balls.items():
            if itemID < 0 or itemID == session.shipid:
                continue
            if ballpark is None:
                break
            slimItem = ballpark.GetInvItem(itemID)
            if slimItem and self.tactical.WantIt(slimItem, filtered, alwaysShown):
                self.tacticalCompass.AddConnector(ball)
            checkStates = self._GetMatchingStates(itemID, self._interestStates)
            checkStates.extend(self._GetMatchingStates(itemID, self._aggressorStates))
            for intrState in checkStates:
                self.CheckState(itemID, intrState, True)

        for ball in self.navBalls:
            self.tacticalCompass.AddConnector(ball)

    def _ClearSelection(self):
        if self.selectedConnector is not None:
            self.selectedConnector.Destroy()
            self.selectedConnector = None
            self.tacticalCompass.SetInterest(None)
        self.selectedID = None

    def _ShowDirectionTo(self, ballID):
        if self.selectedID == ballID:
            return
        self._ClearSelection()
        targetBall = ballpark.GetBall(ballID)
        if targetBall is None:
            return
        self.tacticalCompass.SetInterest(targetBall)
        self.selectedConnector = tacticalUI.CreateStraightConnector(tacticalUI.STYLE_FAINT, tacticalUI.COLOR_GENERIC, None, targetBall)
        self.selectedID = ballID

    def OnShipChange(self):
        if not self.initialized:
            return
        ball = ballpark.GetBall(session.shipid)
        self.tacticalCompass.SetRootBall(ball)

    def UpdateTargetingRange(self):

        def _inner():
            while self.initialized:
                if not session.shipid:
                    if self.tacticalCompass is not None:
                        self.tacticalCompass.compassDisc.HideFiringRange()
                else:
                    ship = sm.GetService('godma').GetItem(session.shipid)
                    if self.tacticalCompass is not None:
                        self.tacticalCompass.SetTargetingRange(ship.maxTargetRange, not self.showingModuleRange)
                        self.actionDisplay.SetMaxMoveRange(self.tacticalCompass.GetMaxRange())
                blue.synchro.SleepSim(1000)

        uthread2.StartTasklet(_inner)

    def UpdateModuleRange(self, module = None, charge = None):
        if not self.initialized:
            return
        self.showingModuleRange = module is not None
        self.tacticalCompass.HideBombRange()
        if module is None:
            self.tacticalCompass.compassDisc.HideFiringRange()
            return
        maxRange, falloff, bombRadius, cynoRadius = self.tactical.FindMaxRange(module, charge)
        if bombRadius:
            self.tacticalCompass.compassDisc.HideFiringRange()
            ball = ballpark.GetBall(session.shipid)
            self.tacticalCompass.ShowBombRange(bombRadius, maxRange, ball)
        elif cynoRadius:
            self.tacticalCompass.compassDisc.HideFiringRange()
            radius = getattr(ballpark.GetBall(session.shipid), 'radius', 0.0)
            self.tacticalCompass.ShowCynoRange(cynoRadius + radius)
        else:
            self.tacticalCompass.SetFiringRange(maxRange, falloff)
