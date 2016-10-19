#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fitting\multiFitWnd.py
from collections import defaultdict
import evetypes
import uthread
from carbon.common.script.sys.serviceConst import ROLE_GMH
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.container import Container
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.control.checkbox import Checkbox
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLarge, EveCaptionSmall, EveCaptionMedium
from eve.client.script.ui.control.eveSinglelineEdit import SinglelineEdit
from eve.client.script.ui.control.eveWindow import Window
import carbonui.const as uiconst
import uix
from eve.client.script.ui.control.progressBar import ProgressBar
from eve.client.script.ui.shared.dockedUI import GetLobbyClass
from eve.common.script.sys.eveCfg import IsDocked
from localization import GetByLabel
from shipfitting.multiBuyUtil import BuyMultipleTypesWithQty
from utillib import KeyVal
from eve.client.script.ui.control.buttons import ButtonIcon
NORMAL_COLOR = (1,
 1,
 1,
 0.75)
WARNING_COLOR = (1,
 0,
 0,
 0.75)
MAX_TOOLTIP_ENTRIES = 10
REFRESH_TEXTUREPATH = 'res:/UI/Texture/Icons/105_32_22.png'
MAX_TEXT_WIDTH = 300
LEFT_EDGE = 10

class MultiFitWnd(Window):
    __guid__ = 'form.MultiFitWnd'
    __notifyevents__ = ['OnSessionChanged']
    default_topParentHeight = 70
    default_height = 400
    default_width = 320
    default_windowID = 'multiFitWnd'
    default_captionLabelPath = 'UI/Fitting/FittingWindow/FittingManagement/MultiFitHeader'
    layoutColumns = 3

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.fitting = None
        self.MakeUnResizeable()
        self.MakeUnstackable()
        self.canFitNum = 0
        self.tryingToFitNum = 1
        self.currentProgress = 0
        self.ConstructUI()
        fitting = attributes.fitting
        self.tryingToFitNum = attributes.get('qty', 1)
        self.LoadWindow(fitting, self.tryingToFitNum)
        self.SetInventoryStatus()
        sm.RegisterNotify(self)

    def ConstructUI(self):
        self.BuildTopParentUI()
        self.AddButtons()
        numColumns = 2
        self.layoutGrid = layoutGrid = LayoutGrid(parent=self.sr.main, columns=numColumns, cellSpacing=(4, 10))
        spacer = Container(pos=(0, 0, 50, 0), align=uiconst.TOPLEFT)
        layoutGrid.AddCell(cellObject=spacer, colSpan=1)
        layoutGrid.FillRow()
        self.BuildNumToFitUI()
        self.BuildWarningUI()
        self.BuildRefreshInventory()
        self.missingLayoutGrid = LayoutGrid(parent=self.layoutGrid, columns=2, cellSpacing=(4, 10))
        self.BuildAvailableShipsUI()
        self.BuildEquipmentUI()
        self.BuildProgressUI()
        self.MakeRigCbUI()

    def BuildTopParentUI(self):
        self.sr.topParent.padding = (2 * const.defaultPadding,
         0,
         2 * const.defaultPadding,
         0)
        self.shipIcon = Icon(name='shipIcon', parent=self.sr.topParent, state=uiconst.UI_NORMAL, size=64, ignoreSize=True)
        self.shipIcon.GetDragData = self.GetFittingDragData
        self.shipIcon.OnClick = self.OpenFitting
        self.shipIcon.hint = GetByLabel('UI/Fitting/ShowFitting')
        self.techSprite = Sprite(name='techIcon', parent=self.sr.topParent, align=uiconst.RELATIVE, width=16, height=16, idx=0)
        self.fitNameEdit = SinglelineEdit(name='fitNameEdit', parent=self.sr.topParent, left=72, width=150, maxLength=20, hint=GetByLabel('UI/Common/ShipName'))
        top = self.fitNameEdit.top + self.fitNameEdit.height + 5
        self.shipNameLabel = EveLabelMedium(name='shipNameLabel', parent=self.sr.topParent, left=77, top=top, state=uiconst.UI_NORMAL)

    def AddButtons(self):
        btnCont = FlowContainer(name='buttonParent', parent=self.sr.main, align=uiconst.TOBOTTOM, padding=6, autoHeight=True, centerContent=True, contentSpacing=uiconst.BUTTONGROUPMARGIN, idx=0)
        text = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/FitShips', numToFit=1)
        self.fitBtn = Button(parent=btnCont, label=text, func=self.DoFitShips, align=uiconst.NOALIGN)
        self.cancelBtn = Button(parent=btnCont, label=GetByLabel('UI/Commands/Cancel'), func=self.Cancel, align=uiconst.NOALIGN)

    def BuildNumToFitUI(self):
        maxShipsAllowed = int(sm.GetService('machoNet').GetGlobalConfig().get('bulkFit_maxShips', 30))
        numCont = Container(name='numCont', align=uiconst.TOTOP, height=30, padLeft=LEFT_EDGE)
        text = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/NumShipsToFit')
        self.numToFitLabel = EveLabelLarge(name='numToFitLabel', parent=numCont, text=text, width=250, autoFitToText=True)
        left = self.numToFitLabel.left + self.numToFitLabel.textwidth + 10
        self.numToFitEdit = SinglelineEdit(name='numToFitEdit', parent=numCont, ints=[1, maxShipsAllowed], OnChange=self.OnNumChanged, left=left, align=uiconst.CENTERLEFT)
        numCont.height = max(self.numToFitLabel.textheight, self.numToFitEdit.height)
        self.layoutGrid.AddCell(cellObject=numCont, colSpan=self.layoutGrid.columns)

    def BuildWarningUI(self):
        self.numWarningLabel = EveCaptionSmall(name='numWarningLabel', state=uiconst.UI_NORMAL, align=uiconst.CENTERTOP, width=MAX_TEXT_WIDTH, autoFitToText=True)
        self.numWarningLabel.SetRGBA(*WARNING_COLOR)
        self.numWarningLabel.LoadTooltipPanel = self.LoadMissingTooltip
        self.layoutGrid.AddCell(cellObject=self.numWarningLabel, colSpan=self.layoutGrid.columns)
        self.layoutGrid.FillRow()

    def BuildRefreshInventory(self):
        self.refreshCont = Transform(parent=self.layoutGrid, pos=(0, 0, 32, 32), align=uiconst.CENTER)
        self.refreshIcon = ButtonIcon(name='refreshSprite', parent=self.refreshCont, width=32, height=32, align=uiconst.CENTER, texturePath=REFRESH_TEXTUREPATH, iconSize=32, func=self.OnRefreshClicked)
        self.refreshIcon.hint = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/RefreshInventoryStatusHint')

    def OnRefreshClicked(self, *args):
        uthread.new(self.refreshCont.StartRotationCycle, cycles=1)
        self.SetInventoryStatus()

    def BuildAvailableShipsUI(self):
        self.shipCounter = EveCaptionMedium(name='shipCounter', parent=self.missingLayoutGrid, state=uiconst.UI_NORMAL, align=uiconst.CENTERRIGHT, left=4)
        self.shipCounter.LoadTooltipPanel = self.LoadShipCounterTooltipPanel
        self.shipCounter.missingDict = {}
        shipText = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/PackagedShipsInHangar')
        self.availableShipsLabel = EveLabelLarge(name='availableShipsLabel', parent=self.missingLayoutGrid, state=uiconst.UI_NORMAL, text=shipText, align=uiconst.CENTERLEFT, width=MAX_TEXT_WIDTH, autoFitToText=True)
        self.availableShipsLabel.hint = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/PackagedShipsInHangarHint')
        self.layoutGrid.FillRow()

    def BuildEquipmentUI(self):
        self.equipmentCounter = EveCaptionMedium(name='equipmentCounter', parent=self.missingLayoutGrid, state=uiconst.UI_NORMAL, align=uiconst.CENTERRIGHT, left=4)
        self.equipmentCounter.LoadTooltipPanel = self.LoadEqCounterTooltipPanel
        self.equipmentCounter.missingDict = {}
        eqText = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/RoundsOfFittingsInHangar')
        self.availableEquipmentLabel = EveLabelLarge(name='availableEquipmentLabel', parent=self.missingLayoutGrid, state=uiconst.UI_NORMAL, text=eqText, align=uiconst.CENTERLEFT, width=MAX_TEXT_WIDTH, autoFitToText=True)
        self.layoutGrid.FillRow()

    def BuildProgressUI(self):
        self.progressCont = Container(parent=self.sr.main, height=36, align=uiconst.TOBOTTOM, padding=(10, 0, 10, 10))
        self.progressCounter = EveCaptionMedium(name='progressCounter', parent=self.progressCont, state=uiconst.UI_NORMAL, align=uiconst.CENTERTOP)
        self.progressBar = ProgressBar(parent=self.progressCont, height=10, align=uiconst.TOBOTTOM)
        self.progressCont.display = False

    def MakeRigCbUI(self):
        checked = settings.user.ui.Get('fitting_rigCB', True)
        text = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/FitRigs')
        self.rigCB = Checkbox(name='rigCB', text=text, OnChange=self.OnCbChanged, left=LEFT_EDGE, checked=checked, prefstype=('user', 'ui'), configName='fitting_rigCB')
        self.rigCB.hint = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/FitRigsHint')
        self.layoutGrid.AddCell(cellObject=self.rigCB, colSpan=self.layoutGrid.columns)

    def OnNumChanged(self, *args):
        self.onNumChangedTimer = AutoTimer(100, self.SetInventoryStatus)

    def OnCbChanged(self, *args):
        self.SetInventoryStatus()

    def OpenFitting(self, *args):
        sm.GetService('fittingSvc').DisplayFitting(self.fitting)

    def LoadWindow(self, fitting, qty = 1):
        self.fitting = fitting
        self.shipCounter.missingDict = {}
        self.equipmentCounter.missingDict = {}
        shipTypeID = fitting.shipTypeID
        self.shipIcon.LoadIconByTypeID(shipTypeID)
        uix.GetTechLevelIcon(self.techSprite, typeID=shipTypeID)
        self.numToFitEdit.text = qty
        self.fitNameEdit.SetValue(fitting.name)
        self.shipNameLabel.text = GetShowInfoLink(shipTypeID, evetypes.GetName(shipTypeID))
        self.SetInventoryStatus()
        self.missingLayoutGrid.RefreshGridLayout()
        self.layoutGrid.RefreshGridLayout()
        layoutWidth, layoutHeight = self.layoutGrid.GetSize()
        newHeight = layoutHeight + self.fitBtn.height + self.progressCont.height + self.sr.topParent.height + 20
        self.height = max(newHeight, self.default_height)
        self.width = max(layoutWidth + 20, self.default_width)

    def SetInventoryStatus(self):
        self.onNumChangedTimer = None
        fitting = self.fitting
        shipTypeID = fitting.shipTypeID
        fittingSvc = sm.GetService('fittingSvc')
        chargesByType, dronesByType, fightersByTypeID, iceByType, itemTypes, modulesByFlag, rigsToFit, subsystems = fittingSvc.GetTypesToFit(fitting, None)
        if rigsToFit:
            self.rigCB.display = True
        else:
            self.rigCB.display = False
        numToFit = self.numToFitEdit.GetValue()
        self.tryingToFitNum = numToFit
        maxAvailableFitting, missingForFullFit = self._GetMaxAvailabeAndMissingForFullFit(itemTypes, modulesByFlag, numToFit)
        nonSingletonShipsNumDict = fittingSvc.GetQt0yInHangarByTypeIDs([shipTypeID], onlyGetNonSingletons=True)
        packagedShipsNum = nonSingletonShipsNumDict.get(shipTypeID, 0)
        self.canFitNum = min(packagedShipsNum, maxAvailableFitting, numToFit)
        btnText = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/FitShips', numToFit=self.canFitNum)
        self.fitBtn.SetLabel(btnText)
        if self.canFitNum < 1:
            self.fitBtn.Disable()
        else:
            self.fitBtn.Enable()
        missingNumShips = max(0, numToFit - packagedShipsNum)
        if missingNumShips:
            missingDict = {shipTypeID: missingNumShips}
        else:
            missingDict = {}
        self.shipCounter.missingDict = missingDict
        if missingForFullFit:
            missingDict = missingForFullFit
        else:
            missingDict = {}
        self.equipmentCounter.missingDict = missingDict
        if missingForFullFit or missingNumShips:
            missingText = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/MissingShipEquipment')
            self.numWarningLabel.text = missingText
        else:
            self.numWarningLabel.text = ''
            self.numWarningLabel.height = 0
        self.SetAvailabilityShipOrEq(self.shipCounter, packagedShipsNum, numToFit)
        self.SetAvailabilityShipOrEq(self.equipmentCounter, maxAvailableFitting, numToFit)

    def _GetMaxAvailabeAndMissingForFullFit(self, itemTypes, modulesByFlag, numToFit):
        fittingSvc = sm.GetService('fittingSvc')
        qtyByTypeID = fittingSvc.GetQt0yInHangarByTypeIDs(itemTypes)
        rigTypeIDs = {t for f, t in modulesByFlag.iteritems() if f in const.rigSlotFlags}
        maxAvailableFitting, missingForFullFit = fittingSvc.GetMaxAvailabeAndMissingForFullFit(True, itemTypes, numToFit, qtyByTypeID, rigTypeIDs)
        return (maxAvailableFitting, missingForFullFit)

    def SetAvailabilityShipOrEq(self, label, available, numToFit):
        label.text = available
        if available < numToFit:
            label.SetRGB(*WARNING_COLOR)
        else:
            label.SetRGB(*NORMAL_COLOR)

    def DoFitShips(self, *args):
        fitting = self.fitting
        fitRigs = self.rigCB.GetValue()
        toActuallyFit = self.canFitNum
        fittingName = self.fitNameEdit.GetValue()
        fittingSvc = sm.GetService('fittingSvc')
        chargesByType, dronesByType, fightersByTypeID, iceByType, itemTypes, modulesByFlag, rigsToFit, subsystems = fittingSvc.GetTypesToFit(fitting, None)
        if fitRigs or not rigsToFit:
            cargoItemsByType = {}
        else:
            cargoItemsByType = defaultdict(int)
            for flagID, typeID in modulesByFlag.iteritems():
                if flagID in const.rigSlotFlags:
                    cargoItemsByType[typeID] += 1

            cargoItemsByType = dict(cargoItemsByType)
        lobby = GetLobbyClass().GetIfOpen()
        if lobby is None:
            return
        lobby.CheckCanAccessService('fitting')
        maxAvailableFitting, missingForFullFit = self._GetMaxAvailabeAndMissingForFullFit(itemTypes, modulesByFlag, toActuallyFit)
        if missingForFullFit:
            self.SetInventoryStatus()
            eve.Message('uiwarning03')
            return
        try:
            self.PrepareForMultiFitCall()
            fittingSvc.DoFitManyShips(chargesByType, dronesByType, fightersByTypeID, fitRigs, fitting, iceByType, cargoItemsByType, toActuallyFit, modulesByFlag, fittingName)
        finally:
            uthread.new(self.ResetUIAfterFitting)

    def PrepareForMultiFitCall(self):
        self.fitBtn.Disable()
        self.cancelBtn.Disable()
        self.currentProgress = 0
        self.progressCounter.text = self.currentProgress
        self.progressCont.display = True
        self.layoutGrid.Disable()
        self.layoutGrid.opacity = 0.2
        sm.RegisterForNotifyEvent(self, 'OnItemChange')

    def ResetUIAfterFitting(self):
        sm.UnregisterForNotifyEvent(self, 'OnItemChange')
        self.currentProgress = 0
        uicore.animations.BlinkOut(self.progressCont, startVal=0.0, endVal=1.0, duration=0.5, loops=3, sleep=True)
        self.progressCont.display = False
        self.progressCounter.text = self.currentProgress
        self.cancelBtn.Enable()
        self.layoutGrid.Enable()
        self.layoutGrid.opacity = 1.0
        self.SetInventoryStatus()

    def Cancel(self, *args):
        self.CloseByUser()

    def GetFittingDragData(self):
        entry = KeyVal()
        entry.fitting = self.fitting
        entry.label = self.fitting.name
        entry.displayText = self.fitting.name
        entry.__guid__ = 'listentry.FittingEntry'
        return [entry]

    def LoadMissingTooltip(self, tooltipPanel, *args):
        text = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/MissingItems', numToFit=self.tryingToFitNum, fittingName=self.fitting.name)
        tooltipPanel.AddLabelLarge(text=text, padBottom=8)
        self.LoadShipCounterTooltipPanel(tooltipPanel, singleGroupShowing=False)
        self.LoadEqCounterTooltipPanel(tooltipPanel, singleGroupShowing=False)
        missingDict = {}
        missingDict.update(self.shipCounter.missingDict)
        missingDict.update(self.equipmentCounter.missingDict)
        self.AddBuyAllBtn(tooltipPanel, missingDict)

    def LoadShipCounterTooltipPanel(self, tooltipPanel, *args, **kwargs):
        missingDict = self.shipCounter.missingDict
        if not missingDict:
            return
        singleGroupShowing = kwargs.get('singleGroupShowing', True)
        text = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/MissingShips', numToFit=self.tryingToFitNum, fittingName=self.fitting.name)
        return self.LoadCounterTooltip(tooltipPanel, missingDict, text, singleGroupShowing)

    def LoadEqCounterTooltipPanel(self, tooltipPanel, *args, **kwargs):
        missingDict = self.equipmentCounter.missingDict
        if not missingDict:
            return
        singleGroupShowing = kwargs.get('singleGroupShowing', True)
        text = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/MissingEquipment', numToFit=self.tryingToFitNum, fittingName=self.fitting.name)
        self.LoadCounterTooltip(tooltipPanel, missingDict, text, singleGroupShowing)

    def LoadCounterTooltip(self, tooltipPanel, missingDict, text, singleGroupShowing = True):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.state = uiconst.UI_NORMAL
        if singleGroupShowing:
            tooltipPanel.AddLabelLarge(text=text, padBottom=8)
        typeList = []
        for eachTypeID, eachQty in missingDict.iteritems():
            typeName = evetypes.GetName(eachTypeID)
            typeList.append((typeName.lower(), (eachTypeID, eachQty)))

        typeList = SortListOfTuples(typeList)
        for eachTypeID, eachQty in typeList[:MAX_TOOLTIP_ENTRIES]:
            typeCont = TooltipEntry(parent=tooltipPanel, typeID=eachTypeID, qty=eachQty)

        if len(typeList) > MAX_TOOLTIP_ENTRIES:
            numItemsNotDisplayed = len(typeList) - MAX_TOOLTIP_ENTRIES
            text = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/MoreItemTypesMissing', numMoreItems=numItemsNotDisplayed)
            tooltipPanel.AddLabelMedium(text=text, align=uiconst.CENTERLEFT)
        if singleGroupShowing:
            self.AddBuyAllBtn(tooltipPanel, missingDict)

    def AddBuyAllBtn(self, tooltipPanel, missingDict):

        def BuyAll(*args):
            BuyMultipleTypesWithQty(missingDict)

        Button(parent=tooltipPanel, label=GetByLabel('UI/Market/MarketQuote/BuyAll'), func=BuyAll, align=uiconst.CENTER)
        if session.role & ROLE_GMH == ROLE_GMH:
            Button(parent=tooltipPanel, label='GM: Give all', func=self.GiveAllGM, align=uiconst.CENTERRIGHT, args=(missingDict,))

    def GiveAllGM(self, missingDict):
        numToCountTo = len(missingDict) + 1
        header = 'GM Item Gift'
        sm.GetService('loading').ProgressWnd(header, '', 1, numToCountTo)
        counter = 1
        for typeID, qty in missingDict.iteritems():
            counter += 1
            sm.GetService('loading').ProgressWnd(header, '', counter, numToCountTo)
            sm.RemoteSvc('slash').SlashCmd('/create %s %s' % (typeID, qty))

        sm.GetService('loading').ProgressWnd('Done', '', numToCountTo, numToCountTo)

    def OnItemChange(self, item, change):
        if item.typeID != self.fitting.shipTypeID:
            return
        if const.ixSingleton in change:
            self.currentProgress += 1
            self.progressCounter.text = '%s / %s' % (self.currentProgress, self.canFitNum)

    def OnSessionChanged(self, isRemote, sess, change):
        if not IsDocked():
            self.CloseByUser()


class TooltipEntry(Container):
    default_height = 32
    default_align = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        typeID = attributes.typeID
        qty = attributes.qty
        iconPadding = 1 * const.defaultPadding
        typeIcon = Icon(name='typeIcon', parent=self, state=uiconst.UI_NORMAL, size=32, left=iconPadding, ignoreSize=True, typeID=typeID)
        techIcon = uix.GetTechLevelIcon(typeID=typeID)
        if techIcon:
            techIcon.left = iconPadding
            techIcon.SetParent(self, idx=0)
        typeName = evetypes.GetName(typeID)
        link = '<url="showinfo:%s">%s</url>' % (typeID, typeName)
        text = '%sx %s' % (qty, link)
        left = iconPadding * 2 + typeIcon.width + 10
        label = EveLabelMedium(parent=self, left=left, text=text, state=uiconst.UI_NORMAL, align=uiconst.CENTERLEFT)
        self.width = label.left + label.textwidth + 10
