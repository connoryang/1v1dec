#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\cef\componentViews\infoComponentView.py
from carbon.common.script.cef.baseComponentView import BaseComponentView

class InfoComponentView(BaseComponentView):
    __guid__ = 'cef.InfoComponentView'
    __COMPONENT_ID__ = const.cef.INFO_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Info'
    __COMPONENT_CODE_NAME__ = 'info'
    NAME_INPUT = 'name'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.NAME_INPUT, '', cls.RECIPE, const.cef.COMPONENTDATA_STRING_TYPE, needsTranslation=True, displayName='Entity Name')


InfoComponentView.SetupInputs()
