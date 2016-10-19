#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\trinity\sceneRenderJobBasic.py
from . import _trinity as trinity
from .sceneRenderJobBase import SceneRenderJobBase

def CreateSceneRenderJobBasic(name = None):
    newRJ = SceneRenderJobBasic()
    if name is not None:
        newRJ.ManualInit(name)
    else:
        newRJ.ManualInit()
    return newRJ


class SceneRenderJobBasic(SceneRenderJobBase):
    renderStepOrder = ['UPDATE_SCENE',
     'SET_VIEWPORT',
     'SET_PROJECTION',
     'SET_VIEW',
     'SET_RENDERTARGET',
     'SET_DEPTH',
     'CLEAR',
     'RENDER_SCENE',
     'UPDATE_TOOLS',
     'RENDER_PROXY',
     'RENDER_INFO',
     'RENDER_VISUAL',
     'RENDER_TOOLS',
     'RESTORE_DEPTH',
     'RESTORE_RENDERTARGET',
     'PRESENT_SWAPCHAIN']

    def _ManualInit(self, name = 'SceneRenderJobInterior'):
        self.ui = None

    def _SetScene(self, scene):
        self.SetStepAttr('UPDATE_SCENE', 'object', scene)
        self.SetStepAttr('RENDER_SCENE', 'scene', scene)

    def _CreateBasicRenderSteps(self):
        self.AddStep('UPDATE_SCENE', trinity.TriStepUpdate(self.GetScene()))
        self.AddStep('RENDER_SCENE', trinity.TriStepRenderScene(self.GetScene()))

    def DoReleaseResources(self, level):
        pass

    def DoPrepareResources(self):
        if self.GetSwapChain():
            self.AddStep('SET_RENDERTARGET', trinity.TriStepPushRenderTarget(self.GetSwapChain().backBuffer))
            self.AddStep('SET_DEPTH', trinity.TriStepPushDepthStencil(self.GetSwapChain().depthStencilBuffer))
            self.AddStep('RESTORE_RENDERTARGET', trinity.TriStepPopRenderTarget())
            self.AddStep('RESTORE_DEPTH', trinity.TriStepPopDepthStencil())
            if not self.HasStep('CLEAR'):
                self.AddStep('CLEAR', trinity.TriStepClear((0.0, 0.0, 0.0, 0.0), 1.0))
        else:
            self.RemoveStep('SET_RENDERTARGET')
            self.RemoveStep('SET_DEPTH')
            self.RemoveStep('RESTORE_RENDERTARGET')
            self.RemoveStep('RESTORE_DEPTH')

    def SetUI(self, ui):
        if ui is None:
            self.RemoveStep('UPDATE_UI')
            self.RemoveStep('RENDER_UI')
        else:
            self.AddStep('UPDATE_UI', trinity.TriStepUpdate(ui))
            self.AddStep('RENDER_UI', trinity.TriStepRenderUI(ui))

    def EnableSceneUpdate(self, isEnabled):
        if isEnabled:
            self.AddStep('UPDATE_SCENE', trinity.TriStepUpdate(self.GetScene()))
        else:
            self.RemoveStep('UPDATE_SCENE')
