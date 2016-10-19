#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\deployment\deploymentCont.py
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.control.eveCombo import Combo
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLarge
from eve.client.script.ui.control.eveSinglelineEdit import PrefixedSingleLineEdit
from eve.client.script.ui.control.eveWindow import Window
import carbonui.const as uiconst
from eve.client.script.ui.control.eveWindowUnderlay import BumpedUnderlay
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.client.script.ui.structure import ChangeSignalConnect
from eve.client.script.ui.structure.structureSettings.schedule.schedulePickeCombo import PickerCombo
from eve.client.script.ui.structure.structureSettings.schedule.vulnerabilitySchedule import VulnerabilitySchedulerWithReinforcement
from eve.client.script.ui.structure.structureSettings.schedule.vulnerabilitySchedulePicker import SchedulePicker
from localization import GetByLabel, CleanImportantMarkup
import structures
import log
import uiutil
STEP_POSITION = 1
STEP_SCHEDULE = 2

class StructureDeploymentWnd(Window):

    @classmethod
    def GetDefaultTop(cls):
        t = uicore.desktop.height / 2 + 100
        return t

    default_caption = GetByLabel('UI/Structures/Deployment/DeploymentHeader')
    default_windowID = 'StructureDeploymentWndID'
    default_width = 430
    default_height = 100
    default_topParentHeight = 0
    default_minSize = (400, 400)
    default_top = GetDefaultTop
    default_left = '__center__'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.MakeUnstackable()
        self.MakeUnResizeable()
        self.MakeUncollapseable()
        self.scheduleStepBuilt = False
        self.structureTypeID = attributes.typeID
        self.height = 100
        self.width = self.default_width
        self.step = STEP_POSITION
        self.controller = attributes.controller
        self.structureDeploymentCont = StructureDeploymentCont(parent=self.sr.main, controller=self.controller, align=uiconst.TOBOTTOM, positionCallback=self.OnPositionBtnClicked, confirmCallback=self.OnConfirmBtnClicked)
        self.structureDeploymentCont.ChangeMouseDisplayFade(faded=False, animated=True)
        requiredHours = sm.GetService('clientDogmaIM').GetDogmaLocation().GetModifiedTypeAttribute(self.structureTypeID, const.attributeVulnerabilityRequired)
        self.mySchedule = structures.Schedule(required=int(requiredHours))
        self.scheduleContParent = Container(parent=self.sr.main, name='scheduleContParent', padding=(10, 4, 10, 4), controller=self.controller)
        self.explanationCont = ContainerAutoSize(parent=self.sr.main, name='explanationCont', alignMode=uiconst.TOTOP, align=uiconst.TOTOP)
        self.BuildExplanationStep()
        self.ChangeSignalConnection()

    def ChangeSignalConnection(self, connect = True):
        entity = sm.GetService('structureDeployment').GetEntity()
        if entity:
            signalAndCallback = [(entity.on_location_updated, self.OnModelLocationUpdated)]
            ChangeSignalConnect(signalAndCallback, connect)

    def BuildExplanationStep(self):
        text = GetByLabel('UI/Structures/Deployment/IntroHeader')
        EveLabelLarge(parent=self.explanationCont, text=text, align=uiconst.TOTOP, padLeft=20, padTop=8)
        text = GetByLabel('UI/Structures/Deployment/DeploymentSteps')
        EveLabelMedium(parent=self.explanationCont, text=text, align=uiconst.TOTOP, padLeft=30)
        self.height = self.GetExplanationHeight()
        isEnabled = True
        entity = sm.GetService('structureDeployment').GetEntity()
        if entity and not entity.IsValidLocation():
            isEnabled = False
        self.structureDeploymentCont.SetPositionEnabledState(isEnabled)

    def GetExplanationHeight(self):
        w, expHeight = self.explanationCont.GetAbsoluteSize()
        newHeight = self.structureDeploymentCont.height + expHeight + self.sr.headerParent.height
        return newHeight

    def BuildScheduleStepIfNeeded(self):
        if not self.scheduleStepBuilt:
            self.scheduleCont = ScheduleCont(parent=self.scheduleContParent, schedule=self.mySchedule, schedulerCallback=self.SchedulerCallback, nameChangedCallback=self.OnNameChanged)
            self.scheduleCont.display = False
            self.scheduleStepBuilt = True
        self.SetConfirmEnabledState(force=True)

    def _OnClose(self, *args, **kw):
        self.controller.CancelDeployment()

    def SchedulerCallback(self, *args):
        self.SetConfirmEnabledState()

    def SetConfirmEnabledState(self, force = False):
        if not force and self.step != STEP_SCHEDULE:
            return
        isEnabled = len(self.scheduleCont.GetGivenName()) >= structures.MIN_STRUCTURE_NAME_LEN and self.mySchedule.IsAllocated()
        self.structureDeploymentCont.SetConfirmEnabledState(isEnabled=isEnabled)

    def OnModelLocationUpdated(self, isValidLocation):
        if self.step != STEP_POSITION:
            return
        self.structureDeploymentCont.SetPositionEnabledState(isValidLocation)

    def OnNameChanged(self, *args):
        self.SetConfirmEnabledState()

    def OnPositionBtnClicked(self, *args):
        if self.step != STEP_POSITION:
            return
        self.SwitchSteps()

    def OnConfirmBtnClicked(self, *args):
        if self.step != STEP_SCHEDULE:
            return
        if not self.mySchedule.IsAllocated():
            uicore.Message('uiwarning03')
            return
        profileSelected = self.scheduleCont.GetSelectedProfile()
        if len(self.scheduleCont.GetGivenName()) < structures.MIN_STRUCTURE_NAME_LEN or not profileSelected:
            return
        self.structureDeploymentCont.SetConfirmEnabledState(isEnabled=False)
        self.controller.ConfirmDeployment(schedule=self.mySchedule, profileID=profileSelected, structureName=self.scheduleCont.GetStructureName())
        self.SetConfirmEnabledState()

    def SwitchSteps(self):
        self.Disable()
        try:
            self._SwitchSteps()
        finally:
            self.Enable()

    def _SwitchSteps(self):
        newStep = self.step + 1
        isMoveMode = True
        self.structureDeploymentCont.SetBtnForStep(newStep)
        if newStep == STEP_POSITION:
            if self.scheduleStepBuilt:
                self.scheduleCont.display = False
            newHeight = self.GetExplanationHeight()
        elif newStep == STEP_SCHEDULE:
            self.explanationCont.display = False
            self._resizeable = True
            self.BuildScheduleStepIfNeeded()
            self.scheduleCont.display = True
            isMoveMode = False
            newHeight = 500
        else:
            return
        self.step = newStep
        self.structureDeploymentCont.ChangeMouseDisplayFade(faded=False, animated=True)
        self.structureDeploymentCont.SetMouseLabels(isMoveMode=isMoveMode)
        newTop = max(0, self.top - (newHeight - self.height))
        uicore.animations.MorphScalar(self.structureDeploymentCont, 'opacity', startVal=0.0, endVal=1.0, duration=0.3, sleep=False)
        uicore.animations.MorphScalar(self, 'top', startVal=self.top, endVal=newTop, duration=0.3, sleep=False)
        uicore.animations.MorphScalar(self, 'height', startVal=self.height, endVal=newHeight, duration=0.3, sleep=True)

    def OnEndScale_(self, *args):
        if self.step == STEP_SCHEDULE:
            self.scheduleCont.GetScheduler().UpdateHourFill()

    def Close(self, *args, **kwds):
        try:
            self.ChangeSignalConnection(connect=False)
        except Exception as e:
            log.LogError('Failed at closing StructureDeploymentWnd in deployment, e = ', e)

        Window.Close(self, *args, **kwds)


class StructureDeploymentCont(Container):
    default_height = 60
    ANCHOR_TOOLTIP = 'UI/Structures/Deployment/AnchorHint'
    ANCHOR_DISABLED_TOOLTIP = 'UI/Structures/Deployment/AnchorDisabledTooltip'
    POSITION_TOOLTIP = 'UI/Structures/Deployment/PositionHint'
    POSITION_DISABLED_TOOLTIP = 'UI/Structures/Deployment/PositionDisbabledHint'
    CANCEL_TOOLTIP = 'UI/Structures/Deployment/CancelHint'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.canConfirm = False
        self.controller = attributes.controller
        positionCallback = attributes.positionCallback
        self.confirmCallback = attributes.confirmCallback
        self.nameChangedCallback = attributes.nameChangedCallback
        leftBtnCont = Container(parent=self, name='leftBtnCont', align=uiconst.TOLEFT, padLeft=10)
        rightBtnCont = Container(parent=self, name='rightBtnCont', align=uiconst.TORIGHT, padRight=10)
        self.positionBtn = Button(name='positionBtn', parent=rightBtnCont, align=uiconst.CENTERLEFT, func=positionCallback, label=GetByLabel('UI/Structures/Deployment/Position'))
        self.positionBtn.stepID = STEP_POSITION
        self.positionBtn.tooltip = self.POSITION_TOOLTIP
        self.positionBtn.tooltipDisabled = self.POSITION_DISABLED_TOOLTIP
        self.anchorBtn = Button(name='anchorBtn', parent=rightBtnCont, align=uiconst.CENTERLEFT, func=self.Confirm, label=GetByLabel('UI/Structures/Deployment/ConfirmDeployment'))
        self.anchorBtn.stepID = STEP_SCHEDULE
        self.anchorBtn.tooltip = self.ANCHOR_TOOLTIP
        self.anchorBtn.tooltipDisabled = self.ANCHOR_DISABLED_TOOLTIP
        self.leftBtns = [self.positionBtn, self.anchorBtn]
        self.SetBtnForStep(STEP_POSITION)
        cancelBtn = Button(name='cancelBtn', parent=leftBtnCont, align=uiconst.CENTERRIGHT, func=self.Cancel, label=GetByLabel('UI/Common/Cancel'), hint=GetByLabel(self.CANCEL_TOOLTIP))
        maxBtnWidth = max(self.positionBtn.width, self.anchorBtn.width, cancelBtn.width)
        leftBtnCont.width = rightBtnCont.width = maxBtnWidth
        self.mouseCont = MouseCont(parent=self)

    def SetMouseLabels(self, isMoveMode = True):
        self.mouseCont.SetMouseLabels(isMoveMode)

    def ChangeMouseDisplayFade(self, faded = False, animated = False):
        if faded:
            opacity = 0.2
        else:
            opacity = 1.0
        if animated:
            uicore.animations.MorphScalar(self.mouseCont, 'opacity', startVal=self.mouseCont.opacity, endVal=opacity, duration=0.3, sleep=False)
        else:
            self.mouseCont.opacity = opacity

    def SetConfirmEnabledState(self, isEnabled):
        self.canConfirm = isEnabled
        self.ChangeBtnStateAndHint(self.anchorBtn, isEnabled)

    def SetPositionEnabledState(self, isEnabled):
        self.ChangeBtnStateAndHint(self.positionBtn, isEnabled)

    def ChangeBtnStateAndHint(self, btn, isEnabled):
        if isEnabled:
            btn.Enable()
            hintPath = btn.tooltip
        else:
            btn.Disable()
            hintPath = btn.tooltipDisabled
        btn.hint = GetByLabel(hintPath)

    def Confirm(self, *args):
        if not self.canConfirm:
            uicore.Message('uiwarning03')
            return
        self.confirmCallback(*args)

    def Cancel(self, *args):
        self.controller.CancelDeployment()

    def SetBtnForStep(self, newStepID):
        for eachBtn in self.leftBtns:
            if eachBtn.stepID == newStepID:
                eachBtn.display = True
            else:
                eachBtn.display = False


class ScheduleCont(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.schedule = attributes.schedule
        self.requiredHours = self.schedule.GetRequiredHours()
        self.schedulerCallback = attributes.schedulerCallback
        self.nameChangedCallback = attributes.nameChangedCallback
        controller = attributes.controller
        self.ChangeSignalConnection()
        self.commonlyUsedPickedCB = None
        self.nameCont = Container(parent=self, name='topCont', align=uiconst.TOTOP, height=40)
        self.topCont = Container(parent=self, name='topCont', align=uiconst.TOTOP, height=40, padTop=10)
        text = GetByLabel('UI/Structures/Deployment/SetVulnerabilityHours')
        self.vulnerabilityLabel = EveLabelMedium(name='explanationLabel', parent=self.topCont, left=4, align=uiconst.TOPLEFT, text=text, top=4)
        helpText = GetByLabel('UI/Structures/Deployment/VulnerabilityHint')
        left = self.vulnerabilityLabel.left + self.vulnerabilityLabel.textwidth + 6
        self.vulnerabilityHelpIcon = MoreInfoIcon(parent=self.topCont, hint=helpText, left=left, top=4, align=uiconst.TOPLEFT)
        self.scheduler = VulnerabilitySchedulerWithReinforcement(parent=self, schedule=self.schedule, callback=self.schedulerCallback)
        self.BuildNameCont()
        self.AddScheduleCombo()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.schedule.OnChange, self.OnScheduleChanged)]
        ChangeSignalConnect(signalAndCallback, connect)

    def BuildNameCont(self):
        padding = 6
        BumpedUnderlay(bgParent=self.nameCont)
        profileCont = Container(parent=self.nameCont, align=uiconst.TORIGHT, left=padding)
        self.profileCombo = Combo(label=GetByLabel('UI/Structures/Deployment/ProfileComboLabel'), parent=profileCont, options=self._GetProfileOptions(), name='profileCombo', width=100, align=uiconst.BOTTOMRIGHT, top=padding)
        profileCont.width = self.profileCombo.width
        nameText = GetByLabel('UI/Structures/Deployment/StructureName')
        self.ssPrefix = '%s - ' % CleanImportantMarkup(cfg.evelocations.Get(session.solarsystemid).locationName)
        self.nameEdit = PrefixedSingleLineEdit(name='nameEdit', parent=self.nameCont, maxLength=32 + len(self.ssPrefix), align=uiconst.TOBOTTOM, padLeft=padding, padRight=30, top=padding, label=nameText, prefix=self.ssPrefix, OnChange=self.nameChangedCallback)
        profileHeight = self.profileCombo.height - self.profileCombo.sr.label.top
        nameHeight = self.nameEdit.height - self.nameEdit.sr.label.top
        newHeight = max(profileHeight, nameHeight) + 2 * padding
        self.nameCont.height = newHeight

    def AddScheduleCombo(self):
        picker = SchedulePicker(requiredHours=self.requiredHours)
        currentSchedules = picker.GetScheduleOptionList()
        if not currentSchedules:
            return
        scheduleOptions = [(GetByLabel('UI/Structures/Deployment/CurrentSchedules'), 0)] + currentSchedules
        self.commonlyUsedPickedCB = PickerCombo(label='', parent=self.topCont, options=scheduleOptions, name='commonlyUsedPickedCB', callback=self.ChangeSchedule, align=uiconst.TOPRIGHT)

    def ChangeSchedule(self, combo, key, val):
        if val == 0:
            return
        self.OnEntryClicked(val)

    def OnScheduleChanged(self, schedule, *args):
        scheduleValue = int(schedule)
        if self.commonlyUsedPickedCB is None:
            return
        if self.commonlyUsedPickedCB.GetValue() != scheduleValue:
            self.commonlyUsedPickedCB.SelectItemByIndex(0)

    def _GetProfileOptions(self):
        structureControllers = sm.GetService('structureControllers').GetAllStructuresProfileController()
        profiles = structureControllers.GetProfiles(createIfMissing=True)
        profileOptions = [ (p.GetProfileName(), profileID, p.GetProfileDescription()) for profileID, p in profiles.iteritems() ]
        profileOptions.sort(key=lambda x: x[0].lower())
        return profileOptions

    def GetSelectedProfile(self):
        selectedID = self.profileCombo.GetValue()
        return selectedID

    def GetStructureName(self):
        return self.nameEdit.GetValue().strip()

    def GetGivenName(self):
        return self.GetStructureName()[len(self.GetNamePrefix()):]

    def GetNamePrefix(self):
        return self.ssPrefix

    def GetScheduler(self):
        return self.scheduler

    def OnEntryClicked(self, vulnerableHours, *args):
        self.schedule.SetVulnerableHours(vulnerableHours)
        self.scheduler.UpdateView()
        if self.schedulerCallback:
            self.schedulerCallback()

    def Close(self):
        try:
            self.ChangeSignalConnection(connect=False)
        except Exception as e:
            log.LogError('Failed at closing ScheduleCont in deployment, e = ', e)

        Container.Close(self)


class MouseCont(Container):
    MOUSE_LEFT_PATH = 'res:/UI/Texture/classes/Achievements/mouseBtnLeft.png'
    MOUSE_RIGHT_PATH = 'res:/UI/Texture/classes/Achievements/mouseBtnRight.png'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        inMoveMode = attributes.get('inMoveMode', True)
        leftMouseCont = Container(parent=self, name='leftMouseCont', align=uiconst.TOLEFT_PROP, width=0.5)
        rightMouseCont = Container(parent=self, name='rightMouseCont', align=uiconst.TORIGHT_PROP, width=0.5)
        leftMouseSprite = Sprite(parent=leftMouseCont, name='leftMouseSprite', align=uiconst.CENTERRIGHT, texturePath=self.MOUSE_LEFT_PATH, pos=(0, 0, 32, 32))
        rightMouseSprite = Sprite(parent=rightMouseCont, name='rightMouseSprite', align=uiconst.CENTERLEFT, texturePath=self.MOUSE_RIGHT_PATH, pos=(0, 0, 32, 32))
        self.leftLabel = EveLabelMedium(parent=leftMouseCont, name='leftLabel', align=uiconst.CENTERRIGHT, pos=(32, -6, 0, 0))
        self.rightLabel = EveLabelMedium(parent=rightMouseCont, name='rightLabel', align=uiconst.CENTERLEFT, pos=(32, -6, 0, 0))
        self.SetMouseLabels(inMoveMode)

    def SetMouseLabels(self, isMoveMode = True):
        if isMoveMode:
            leftLabelPath = 'UI/Structures/Deployment/MoveStructure'
            rightLabelPath = 'UI/Structures/Deployment/RotateStructure'
        else:
            leftLabelPath = 'UI/Structures/Deployment/AddHours'
            rightLabelPath = 'UI/Structures/Deployment/RemoveHours'
        self.leftLabel.text = GetByLabel(leftLabelPath)
        self.rightLabel.text = GetByLabel(rightLabelPath)
