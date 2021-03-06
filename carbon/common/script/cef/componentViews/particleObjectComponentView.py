#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\cef\componentViews\particleObjectComponentView.py
from carbon.common.script.cef.baseComponentView import BaseComponentView

class ParticleObjectComponentView(BaseComponentView):
    __guid__ = 'cef.ParticleObjectComponentView'
    __COMPONENT_ID__ = const.cef.PARTICLE_OBJECT_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Particle Object'
    __COMPONENT_CODE_NAME__ = 'particleObject'
    __SHOULD_SPAWN__ = {'client': True}
    RED_FILE = 'redFile'
    POSITION_OFFSET = 'positionOffset'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.RED_FILE, '', cls.RECIPE, const.cef.COMPONENTDATA_STRING_TYPE, displayName='Red File')
        cls._AddInput(cls.POSITION_OFFSET, '(0.0,0.0,0.0)', cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE, displayName='Position Offset')
        cls._AddInput('depthOffset', 0.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Transparency Depth Offset')
        cls._AddInput('maxParticleRadius', 0.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Maximum Particle Radius')
        cls._AddInput('shBoundsMin', '(0.0,0.0,0.0)', cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE, displayName='SH Box Bounds Min')
        cls._AddInput('shBoundsMax', '(0.0,0.0,0.0)', cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE, displayName='SH Box Bounds Max')


ParticleObjectComponentView.SetupInputs()
