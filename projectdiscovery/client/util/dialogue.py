#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\projectdiscovery\client\util\dialogue.py
import carbonui.const as uiconst
import localization
import uicontrols
import uiprimitives
from eve.client.script.ui.control.eveLabel import EveLabelLargeBold
from projectdiscovery.client.const import Events as projectDiscoveryEvents
TEXT_HEADER_HEIGHT = 20
HEADER_CONTAINER_HEIGHT = 25
BOTTOM_CONTAINER_HEIGHT = 40
MIN_MESSAGE_TEXT_HEIGHT = 220

class Dialogue(uiprimitives.Container):
    default_bgColor = (0, 0, 0, 1)

    def ApplyAttributes(self, attributes):
        super(Dialogue, self).ApplyAttributes(attributes)
        self.label = attributes.get('label')
        self.message_header_text = attributes.get('messageHeaderText')
        self.message_text = attributes.get('messageText')
        self.button_label = attributes.get('buttonLabel')
        self.toHide = attributes.get('toHide')
        self.isTutorial = attributes.get('isTutorial')
        self._close_event = attributes.get('onCloseEvent', projectDiscoveryEvents.EnableUI)
        if self.toHide:
            self.toHide.opacity = 0.5
        self.construct_layout()

    def construct_layout(self):
        uicontrols.Frame(name='main_frame', parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/SampleBack.png', cornerSize=20, padLeft=-8, padTop=-8, padRight=-8, padBottom=-8)
        header_container = uiprimitives.Container(name='headerContainer', parent=self, height=HEADER_CONTAINER_HEIGHT, align=uiconst.TOTOP)
        uicontrols.Label(name='headerLabel', parent=header_container, align=uiconst.CENTERLEFT, left=10, text=self.label)
        main_container = uiprimitives.Container(name='mainContainer', parent=self, align=uiconst.TOTOP)
        agent_container = uiprimitives.Container(name='agentContainer', parent=main_container, align=uiconst.TOPLEFT, height=170, width=150, left=10, top=5)
        uiprimitives.Sprite(name='agentImage', parent=agent_container, align=uiconst.TOTOP, height=150, width=150, texturePath='res:/UI/Texture/classes/ProjectDiscovery/lundberg.jpg')
        uicontrols.Label(name='agentName', parent=agent_container, align=uiconst.TOTOP, text=localization.GetByLabel('UI/ProjectDiscovery/AgentName'), top=5)
        uiprimitives.Sprite(name='SOE_logo', parent=main_container, align=uiconst.BOTTOMLEFT, height=75, width=75, texturePath='res:/UI/Texture/Corps/14_128_1.png', top=-10)
        text_container = uiprimitives.Container(name='textContainer', parent=main_container, align=uiconst.TORIGHT, width=270, left=10)
        text_header_container = uiprimitives.Container(name='textHeaderContainer', parent=text_container, align=uiconst.TOTOP, height=TEXT_HEADER_HEIGHT)
        EveLabelLargeBold(parent=text_header_container, align=uiconst.CENTERLEFT, text=self.message_header_text)
        text_message_container = uiprimitives.Container(name='text_message_container', parent=text_container, align=uiconst.TOTOP)
        main_message = uicontrols.Label(parent=text_message_container, align=uiconst.TOTOP, text=self.message_text, top=5)
        bottom_container = uiprimitives.Container(name='bottomContainer', parent=self, height=BOTTOM_CONTAINER_HEIGHT, align=uiconst.TOBOTTOM)
        self.close_button = uicontrols.Button(name='close_button', parent=bottom_container, fontsize=14, fixedwidth=125, fixedheight=22, label=self.button_label, align=uiconst.BOTTOMRIGHT, top=10, left=10, func=lambda x: self.close())
        if self.isTutorial:
            self.skip_button = uicontrols.Button(name='skipButton', parent=bottom_container, fontsize=14, fixedwidth=125, fixedheight=22, label='Skip Tutorial', align=uiconst.CENTERBOTTOM, top=10, left=10, func=lambda x: self.skip_tutorial())
        message_height = max(MIN_MESSAGE_TEXT_HEIGHT, main_message.height)
        text_message_container.height = message_height
        self.height = message_height + TEXT_HEADER_HEIGHT + HEADER_CONTAINER_HEIGHT + BOTTOM_CONTAINER_HEIGHT
        main_container.height = message_height + TEXT_HEADER_HEIGHT

    def close(self):
        if self.isTutorial:
            sm.ScatterEvent(projectDiscoveryEvents.StartTutorial)
        if self.toHide:
            self.toHide.opacity = 1
        sm.ScatterEvent(self._close_event)
        self.Close()

    def skip_tutorial(self):
        if self.toHide:
            self.toHide.opacity = 1
        sm.ScatterEvent(projectDiscoveryEvents.ProjectDiscoveryStarted, False)
        self.Close()
