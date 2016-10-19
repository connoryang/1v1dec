#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\charsheet\bioPanel.py
import uthread
from carbon.common.script.util.commonutils import StripTags
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from localization import GetByLabel
MAXBIOLENGTH = 1000

class BioPanel(Container):
    default_name = 'BioPanel'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.bioClient = None
        self.edit = EditPlainText(parent=self, maxLength=MAXBIOLENGTH, showattributepanel=1, padding=(0,
         const.defaultPadding,
         0,
         const.defaultPadding))

    def LoadBioFromServer(self):
        self.bioServer = ''
        if not self.bioClient:
            bio = sm.RemoteSvc('charMgr').GetCharacterDescription(session.charid)
            if bio is not None:
                self.bioClient = bio
            else:
                self.bioClient = ''
        if self.bioClient:
            self.bioServer = self.bioClient

    def LoadPanel(self, *args):
        self.LoadBioFromServer()
        bio = self.bioServer or GetByLabel('UI/CharacterSheet/CharacterSheetWindow/BioEdit/HereYouCanTypeBio')
        self.edit.SetValue(bio)

    def AutoSaveBio(self):
        newbio = self.edit.GetValue()
        defaultBioString = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/BioEdit/HereYouCanTypeBio')
        newbio = newbio.replace(defaultBioString, '')
        if not len(StripTags(newbio)):
            newbio = ''
        self.bioClient = newbio
        if newbio.strip() != self.bioServer:
            uthread.new(self._AutoSaveBio, newbio)
            self.bioServer = newbio

    def _AutoSaveBio(self, newbio):
        sm.RemoteSvc('charMgr').SetCharacterDescription(newbio)

    def UnloadPanel(self):
        self.AutoSaveBio()

    def Close(self):
        if self.display:
            self.AutoSaveBio()
        Container.Close(self)
