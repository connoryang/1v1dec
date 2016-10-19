#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\devtools\script\renderjobprofiler.py
import blue
from carbonui.primitives.container import Container
from carbonui import const as uiconst
import trinity
import uthread2
from eve.client.script.ui.control.eveWindow import Window
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveCombo import Combo
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.buttons import Button
import eve.client.script.ui.control.entries as listentry
PANEL_HEIGHT = 250
PANEL_WIDTH = 450

class RenderJobProfiler(Window):
    default_width = PANEL_WIDTH
    default_height = PANEL_HEIGHT
    default_minSize = (default_width, default_height)

    def ApplyAttributes(self, attributes):
        super(RenderJobProfiler, self).ApplyAttributes(attributes)
        self.SetCaption('Render Job Profiler')
        self._renderJob = None
        self.SetTopparentHeight(0)
        parent = self.GetMainArea()
        parent.SetAlign(uiconst.TOALL)
        parent.padding = 5
        top = Container(parent=parent, align=uiconst.TOTOP, height=20)
        Label(text='Render Job', parent=top, align=uiconst.TOLEFT, padding=4)
        combo = Combo(parent=top, options=[ (rj.name, rj) for rj in trinity.renderJobs.recurring ], callback=self._OnRenderJob, align=uiconst.TOALL)
        bottom = Container(parent=parent, align=uiconst.TOBOTTOM, height=20, padding=2)
        Button(parent=bottom, align=uiconst.CENTER, label='Copy', func=self._Copy, args=())
        self._scroll = Scroll(parent=parent, align=uiconst.TOALL, top=4)
        self._OnRenderJob(None, None, combo.selectedValue)
        uthread2.StartTasklet(self._UpdateTiming)

    def _Copy(self):
        if not self._renderJob:
            return
        table = '\n'.join(('{0}\t{1:.4f}\t{2:.4f}'.format(step.name or type(step).__name__, step.cpuTime, step.gpuTime) for step in self._renderJob.steps))
        print table
        blue.pyos.SetClipboardData(table)

    def _UpdateTiming(self):
        while self.state != uiconst.UI_HIDDEN:
            for each in self._scroll.GetNodes():
                if each['panel']:
                    step = each['step']
                    each['panel'].sr.label.text = '{0}<t>{1:.4f}<t>{2:.4f}'.format(step.name or type(step).__name__, step.cpuTime, step.gpuTime)

            uthread2.Sleep(0.03)

    def _OnRenderJob(self, _, __, value):
        if value == self._renderJob:
            return
        if self._renderJob:
            for step in self._renderJob.steps:
                step.debugCaptureCpuTime = False
                step.debugCaptureGpuTime = False

        self._renderJob = value
        contentList = []
        if value:
            for step in value.steps:
                step.debugCaptureCpuTime = True
                step.debugCaptureGpuTime = True
                contentList.append(listentry.Get('Generic', {'label': '%s<t><t>' % (step.name or type(step).__name__),
                 'step': step}))

        self._scroll.Load(contentList=contentList, headers=['Step', 'CPU Time', 'GPU Time'], fixedEntryHeight=18)
