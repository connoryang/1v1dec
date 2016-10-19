#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\inventorycommon\holdTracker.py
import inventorycommon.const as inventoryConst
MAX_HOLD_FILL_DISPLAY_RATIO = 1.0

class HoldTracker(object):
    __notifyevents__ = ['OnCapacityChange', 'OnItemChangeProcessed']

    def __init__(self, cargoButton, trackingSettings, getControllerFromIDFunc):
        self.myShipID = None
        self.myShipTypeID = None
        self.cargoHold = None
        self.button = cargoButton
        self.holds = {}
        self.settings = trackingSettings
        self.mainHoldName = self.GetPreferredCargoHold()
        self.lastKnownCapacity = None
        self.lastKnownUsed = None
        self.GetControllerFromIDFunc = getControllerFromIDFunc
        self.Initialize()

    def Initialize(self):
        self.UpdateForCurrentShip()
        self.InitialUpdate()

    def Destroy(self):
        sm.UnregisterNotify(self)
        self.myShipID = None
        self.cargoHold = None
        self.holds = {}
        self.mainHoldName = inventoryConst.shipCargoHold

    def GetPreferredCargoHold(self):
        return self.settings.GetTrackedHoldForShip()

    def SavePreferredHoldName(self, holdName):
        self.settings.SaveTrackedHoldForShip(holdName)

    def SetMainCargoHold(self, holdName):
        self.Destroy()
        self.mainHoldName = holdName
        self.SavePreferredHoldName(holdName)
        self.Initialize()

    def Register(self):
        sm.RegisterNotify(self)

    def UpdateForCurrentShip(self):
        self.myShipID = session.shipid
        self.myShipTypeID = sm.GetService('godma').GetItem(session.shipid).typeID
        self.FetchInventoryControllers()
        self.Register()

    def FetchInventoryControllers(self):
        myHolds = self.GetMyHolds()
        for holdName in myHolds:
            hold = self.GetControllerFromIDFunc((holdName, self.myShipID))
            self.holds[holdName] = hold
            if holdName == self.mainHoldName:
                self._SetMainHold(hold)

    def GetMyHolds(self):
        godmaType = sm.GetService('godma').GetStateManager().GetType(self.myShipTypeID)
        myHolds = inventoryConst.GetHoldsInType(godmaType)
        return myHolds

    def _SetMainHold(self, hold):
        self.cargoHold = hold

    def _SaveCapacityForTrackedHold(self):
        if self.cargoHold:
            capacity = self._GetTrackedCapacity()
            self.lastKnownCapacity = capacity.capacity
            self.lastKnownUsed = capacity.used

    def _HasAnythingChanged(self):
        capacity = self._GetTrackedCapacity()
        return self.lastKnownCapacity != capacity.capacity or self.lastKnownUsed != capacity.used

    def UpdatePercentage(self):
        self.button.SetFillRatio(ratio=self._GetHoldFillDisplayRatio())

    def GetInventoryIDs(self):
        inv = []
        for inventory in self.holds.itervalues():
            inv.append(inventory.itemID)

        return inv

    def _GetHoldFillDisplayRatio(self):
        if self.cargoHold:
            capacity = self._GetTrackedCapacity()
            holdFillDisplayRatio = min(self._GetRatioFromCapacity(capacity), MAX_HOLD_FILL_DISPLAY_RATIO)
            return holdFillDisplayRatio
        return 0

    def _GetTrackedCapacity(self):
        return self.cargoHold.GetCapacity()

    def _GetRatioFromCapacity(self, capacity):
        if capacity.capacity == 0:
            return 0
        used = capacity.used
        totalcap = capacity.capacity
        ratio = used / totalcap
        return ratio

    def GetHoldsDictionary(self):
        holds = {}
        for name, invController in self.holds.iteritems():
            holds[name] = ('{:.2%}'.format(self._GetRatioFromCapacity(invController.GetCapacity())), invController.locationFlag)

        return holds

    def Blink(self):
        shouldBlink = self.settings.IsCargoHoldBlinkEnabled()
        if self.button and shouldBlink:
            self.button.BlinkWhite()

    def InitialUpdate(self):
        self._SaveCapacityForTrackedHold()
        self.UpdatePercentage()

    def OnCapacityChange(self, moduleID):
        self.BlinkAndUpdateIfChanged()

    def BlinkAndUpdateIfChanged(self):
        if self._HasAnythingChanged():
            self._SaveCapacityForTrackedHold()
            self.Blink()
            self.UpdatePercentage()

    def OnItemChangeProcessed(self, item = None, change = None):
        doBlinkAndStuff = False
        inventoryIDS = self.GetInventoryIDs()
        if item and item.locationID in self.GetInventoryIDs():
            doBlinkAndStuff = True
        elif change:
            for holdID in change.values():
                if holdID in inventoryIDS:
                    doBlinkAndStuff = True
                    break

        if doBlinkAndStuff:
            self.BlinkAndUpdateIfChanged()
