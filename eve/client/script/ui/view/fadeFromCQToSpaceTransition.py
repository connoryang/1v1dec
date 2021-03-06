#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\view\fadeFromCQToSpaceTransition.py
import blue
import uiprimitives
import viewstate
import carbonui.const as uiconst
import util

class FadeFromCQToSpaceTransition(viewstate.Transition):
    __guid__ = 'viewstate.FadeFromCQToSpaceTransition'

    def __init__(self, fadeTimeMS = 1000, fadeInTimeMS = None, fadeOutTimeMS = None, **kwargs):
        viewstate.Transition.__init__(self, **kwargs)
        self.fadeInTimeMS = fadeInTimeMS or fadeTimeMS
        self.fadeOutTimeMS = fadeOutTimeMS or fadeTimeMS
        self.fadeLayer = None

    def StartTransition(self, fromView, toView):
        viewstate.Transition.StartTransition(self, fromView, toView)
        viewState = sm.GetService('viewState')
        self.fadeLayer = uiprimitives.Container(name='transition_overlay', parent=viewState.overlayLayerParent, pickState=uiconst.TR2_SPS_OFF, bgColor=util.Color.BLACK, opacity=0.0)
        uicore.animations.FadeIn(self.fadeLayer, duration=self.fadeInTimeMS / 1000.0, sleep=True)

    def EndTransition(self, fromView, toView):
        michelle = sm.GetService('michelle')
        ball = michelle.GetBall(session.shipid)
        while ball is None or getattr(ball, 'model', None) is None or not ball.model.display:
            blue.synchro.Yield()
            ball = michelle.GetBall(session.shipid)

        sm.GetService('loading').FadeOut(self.fadeOutTimeMS, opacityStart=1.0)
        uicore.animations.FadeOut(self.fadeLayer, duration=self.fadeOutTimeMS / 1000.0, sleep=True)
        self.fadeLayer.Close()
        del self.fadeLayer
        viewstate.Transition.EndTransition(self, fromView, toView)
