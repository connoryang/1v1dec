#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\charsheet\attributesPanel.py
from carbonui.primitives.container import Container
from eve.client.script.ui.control import entries
from eve.client.script.ui.control.eveScroll import Scroll
from eve.common.script.sys.dbrow import LookupConstValue
from localization import GetByLabel
from utillib import KeyVal

class AttributesPanel(Container):
    default_name = 'AttributesPanel'
    __notifyevents__ = ['OnAttribute', 'OnAttributes', 'OnRespecInfoUpdated']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.scroll = Scroll(parent=self, padding=(0, 4, 0, 4))
        self.scroll.sr.id = 'charsheet_myattributes'

    def LoadPanel(self, *args):
        scrollList = sm.GetService('info').GetAttributeScrollListForItem(itemID=session.charid, typeID=const.typeCharacterAmarr, attrList=[const.attributePerception,
         const.attributeMemory,
         const.attributeWillpower,
         const.attributeIntelligence,
         const.attributeCharisma])
        respecInfo = sm.GetService('skills').GetRespecInfo()
        self.respecEntry = entries.Get('AttributeRespec', data=KeyVal(nextTimedRespec=respecInfo['nextTimedRespec'], freeRespecs=respecInfo['freeRespecs']))
        scrollList.append(self.respecEntry)
        self.scroll.Load(fixedEntryHeight=32, contentList=scrollList, noContentHint=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/NoAttributesFound'))

    def UpdateInline(self, attributeID, value):
        for entry in self.scroll.GetNodes():
            if entry.attributeID == attributeID:
                entry.text = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/Points', skillPoints=int(value))
                if entry.panel:
                    entry.panel.sr.text.text = entry.text
                    entry.panel.hint = entry.text.replace('<t>', '  ')

    def OnAttribute(self, attributeName, item, value):
        if not self.display:
            return
        if attributeName in ('memory', 'intelligence', 'willpower', 'perception', 'charisma'):
            self.UpdateInline(LookupConstValue('attribute%s' % attributeName.capitalize(), 0), value)

    def OnAttributes(self, changes):
        for attributeName, item, value in changes:
            self.OnAttribute(attributeName, item, value)

    def OnRespecInfoUpdated(self):
        if self.display:
            self.LoadPanel()
