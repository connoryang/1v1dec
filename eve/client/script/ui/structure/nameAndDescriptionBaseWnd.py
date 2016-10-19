#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\nameAndDescriptionBaseWnd.py
from carbonui import const as uiconst, const
from eve.client.script.ui.control.buttonGroup import ButtonGroup
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.control.eveSinglelineEdit import SinglelineEdit
from eve.client.script.ui.control.eveWindow import Window
from localization import GetByLabel

class NameAndDescBaseWnd(Window):
    default_name = 'nameAndDescBaseWnd'
    default_windowID = 'NameAndDescBaseWnd'
    default_width = 200
    default_height = 200
    default_topParentHeight = 0
    confirmLabelPath = ''
    nameLabelPath = ''
    descriptionLabelPath = ''

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.MakeUnResizeable()
        self.controller = attributes.controller
        self.btnGroup = ButtonGroup(parent=self.sr.main, idx=0, line=True)
        self.btnGroup.AddButton(GetByLabel(self.confirmLabelPath), self.OnConfirmClicked)
        self.btnGroup.AddButton(GetByLabel('UI/Commands/Cancel'), self.Cancel)
        self.groupNameField = SinglelineEdit(parent=self.sr.main, align=uiconst.TOTOP, label=GetByLabel(self.nameLabelPath), padding=4, top=10, maxLength=30)
        EveLabelSmall(name='titleHeader', parent=self.sr.main, text=GetByLabel(self.descriptionLabelPath), align=uiconst.TOTOP, top=6, padLeft=4)
        self.groupDescField = EditPlainText(parent=self.sr.main, padding=(4, 0, 4, 4), maxLength=200)
        self.PopulateFields()

    def PopulateFields(self):
        pass

    def OnConfirmClicked(self, *args):
        name = self.groupNameField.GetValue().strip()
        desc = self.groupDescField.GetValue().strip()
        if name:
            self.Confirm(name, desc)
            self.CloseByUser()
        else:
            uicore.Message('uiwarning03')

    def Confirm(self, name, desc):
        pass

    def Cancel(self, *args):
        self.CloseByUser()
