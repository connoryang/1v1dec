#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\charsheet\plexPanel.py
import uthread
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer, CONTENT_ALIGN_CENTER
from carbonui.util.color import Color
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLargeBold, EveLabelMediumBold
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.shared.monetization.events import LogCharacterSheetPilotLicenseImpression
import carbonui.const as uiconst
from eve.client.script.ui.shared.vgs.button import BuyButtonIsk, BuyButtonPlex
from localization import GetByLabel

class PLEXPanel(Container):
    default_name = 'PLEXPanel'
    __notifyevents__ = ['OnMultipleCharactersTrainingRefreshed']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.isConstructed = False

    def LoadPanel(self, *args):
        self.ConstructLayout()
        self.multipleQueueLabel1.text = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/AdditionalQueueNotActive')
        self.multipleQueueLabel1.color = Color.GRAY5
        self.multipleQueueExpiryLabel1.state = uiconst.UI_HIDDEN
        self.multipleQueueIcon1.opacity = 0.3
        self.multipleQueueLabel2.text = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/AdditionalQueueNotActive')
        self.multipleQueueLabel2.color = Color.GRAY5
        self.multipleQueueExpiryLabel2.state = uiconst.UI_HIDDEN
        self.multipleQueueIcon2.opacity = 0.3
        for index, (trainingID, trainingExpiry) in enumerate(sorted(sm.GetService('skillqueue').GetMultipleCharacterTraining().iteritems())):
            if index == 0:
                self.multipleQueueLabel1.text = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/AdditionalQueueActive')
                self.multipleQueueLabel1.color = (0.0, 1.0, 0.0, 0.8)
                self.multipleQueueExpiryLabel1.text = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/AdditionalQueueExpires', expiryDate=trainingExpiry)
                self.multipleQueueExpiryLabel1.state = uiconst.UI_DISABLED
                self.multipleQueueIcon1.opacity = 1.0
            elif index == 1:
                self.multipleQueueLabel2.text = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/AdditionalQueueActive')
                self.multipleQueueLabel2.color = (0.0, 1.0, 0.0, 0.8)
                self.multipleQueueExpiryLabel2.text = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/AdditionalQueueExpires', expiryDate=trainingExpiry)
                self.multipleQueueExpiryLabel2.state = uiconst.UI_DISABLED
                self.multipleQueueIcon2.opacity = 1.0

        if self.GetSubscriptionDays():
            self.plexSubscriptionLabel.text = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/DaysLeft', daysLeft=self.GetSubscriptionDays())
        else:
            self.plexSubscriptionLabel.text = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/Fine')

    def ConstructLayout(self):
        if self.isConstructed:
            return
        self.isConstructed = True
        scrollContainer = ScrollContainer(name='plexScroll', parent=self, align=uiconst.TOALL, padding=(10, 10, 10, 10))
        EveLabelLargeBold(parent=scrollContainer, align=uiconst.TOTOP, text=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/PlexTitle'), padding=(10, 10, 0, 0))
        EveLabelMedium(parent=scrollContainer, align=uiconst.TOTOP, text=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/PlexDescription'), padding=(10, 2, 0, 10), color=Color.GRAY5)
        subscription = ContainerAutoSize(parent=scrollContainer, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, bgColor=(0, 0, 0, 0.3))
        self.plexSubscriptionLabel = EveLabelMedium(parent=subscription, align=uiconst.TOTOP, text='', padding=(75, 15, 0, 15))
        InfoIcon(parent=subscription, typeID=const.typePilotLicence, pos=(10, 2, 55, 55), texturePath='res:/UI/Texture/Icons/plex.png', iconOpacity=1.0)
        InfoIcon(parent=subscription, align=uiconst.TOPRIGHT, typeID=const.typePilotLicence, top=10, left=10)
        EveLabelLargeBold(parent=scrollContainer, align=uiconst.TOTOP, text=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/BuyingPlexTitle'), padding=(10, 10, 0, 0))
        EveLabelMedium(parent=scrollContainer, align=uiconst.TOTOP, text=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/BuyingPlexDescription'), padding=(10, 2, 0, 10), color=Color.GRAY5)
        buyButtons = FlowContainer(parent=scrollContainer, align=uiconst.TOTOP, contentAlignment=CONTENT_ALIGN_CENTER, contentSpacing=(8, 0))
        BuyButtonIsk(parent=buyButtons, align=uiconst.NOALIGN, typeID=const.typePilotLicence)
        BuyButtonPlex(parent=buyButtons, align=uiconst.NOALIGN, logContext='CharacterSheet')
        EveLabelLargeBold(parent=scrollContainer, align=uiconst.TOTOP, text=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/MultipleCharacterTitle'), padding=(10, 25, 0, 0))
        EveLabelMedium(parent=scrollContainer, align=uiconst.TOTOP, text=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/MultipleCharacterDescription'), padding=(10, 2, 0, 10), color=Color.GRAY5)
        multipleQueue1 = ContainerAutoSize(parent=scrollContainer, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, bgColor=(0, 0, 0, 0.3))
        self.multipleQueueLabel1 = EveLabelMediumBold(parent=multipleQueue1, align=uiconst.TOTOP, text='', padding=(35, 8, 0, 8))
        self.multipleQueueExpiryLabel1 = EveLabelMediumBold(parent=multipleQueue1, align=uiconst.TOPRIGHT, text='', pos=(10, 8, 0, 0), color=Color.GRAY5)
        self.multipleQueueIcon1 = Icon(parent=multipleQueue1, align=uiconst.TOPLEFT, icon='res:/UI/Texture/Icons/additional_training_queue.png', pos=(10, 7, 17, 17))
        multipleQueue2 = ContainerAutoSize(parent=scrollContainer, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, bgColor=(0, 0, 0, 0.3))
        self.multipleQueueLabel2 = EveLabelMediumBold(parent=multipleQueue2, align=uiconst.TOTOP, text='', padding=(35, 8, 0, 8))
        self.multipleQueueExpiryLabel2 = EveLabelMediumBold(parent=multipleQueue2, align=uiconst.TOPRIGHT, text='', pos=(10, 8, 0, 0), color=Color.GRAY5)
        self.multipleQueueIcon2 = Icon(parent=multipleQueue2, align=uiconst.TOPLEFT, icon='res:/UI/Texture/Icons/additional_training_queue.png', pos=(10, 7, 17, 17))
        EveLabelLargeBold(parent=scrollContainer, align=uiconst.TOTOP, text=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/ConvertAurumTitle'), padding=(10, 25, 0, 0))
        EveLabelMedium(parent=scrollContainer, align=uiconst.TOTOP, text=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/ConvertAurumDescription'), padding=(10, 2, 0, 0), color=Color.GRAY5)
        if boot.region != 'optic':
            EveLabelLargeBold(parent=scrollContainer, align=uiconst.TOTOP, text=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/CharacterTransferTitle'), padding=(10, 25, 0, 0))
            EveLabelMedium(parent=scrollContainer, align=uiconst.TOTOP, text=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/CharacterTransferDescription'), padding=(10, 2, 0, 0), color=Color.GRAY5)
        FillThemeColored(parent=self, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.1)

    def GetSubscriptionDays(self):
        return sm.GetService('charactersheet').GetSubscriptionDays()

    def OnMultipleCharactersTrainingRefreshed(self):
        if self.display:
            self.LoadPilotLicensePanel()


def LogOpenPilotLicense():
    uthread.new(LogCharacterSheetPilotLicenseImpression())
