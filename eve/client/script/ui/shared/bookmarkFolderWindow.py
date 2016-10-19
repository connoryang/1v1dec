#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\bookmarkFolderWindow.py
import uicls
import carbonui.const as uiconst
import localization
import uiprimitives
import uicontrols
import util

class BookmarkFolderWindow(uicontrols.Window):
    __guid__ = 'form.BookmarkFolderWindow'
    default_topParentHeight = 0

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        self.folder = attributes.get('folder', None)
        self.ownerID = None
        if self.folder is None:
            self.SetCaption(localization.GetByLabel('UI/PeopleAndPlaces/NewFolder'))
            self.isNew = True
        else:
            self.SetCaption(localization.GetByLabel('UI/PeopleAndPlaces/EditFolder'))
            self.isNew = False
        self.SetMinSize([280, 110])
        main = uiprimitives.Container(name='main', parent=self.sr.main, align=uiconst.TOALL, left=4, width=4)
        labelContainer = uiprimitives.Container(name='labelContainer', parent=main, align=uiconst.TOTOP, top=8, height=20, padding=(2, 2, 2, 2))
        uicontrols.EveLabelMedium(text=localization.GetByLabel('UI/PeopleAndPlaces/Name'), parent=labelContainer, align=uiconst.TOLEFT, width=60)
        self.nameEdit = uicontrols.SinglelineEdit(name='nameEdit', setvalue=self.folder.folderName if self.folder else '', parent=labelContainer, align=uiconst.TOALL, width=0)
        self.nameEdit.OnReturn = self.Confirm
        sectionContainer = uiprimitives.Container(name='sectionContainer', parent=main, align=uiconst.TOTOP, top=8, height=20, padding=(2, 2, 2, 2))
        uicontrols.EveLabelMedium(text=localization.GetByLabel('UI/PeopleAndPlaces/LocationSection'), parent=sectionContainer, align=uiconst.TOLEFT, width=60)
        if not self.isNew or util.IsNPCCorporation(session.corpid):
            if not self.isNew and self.folder.ownerID == session.corpid:
                sectionName = localization.GetByLabel('UI/PeopleAndPlaces/CorporationLocations')
                self.ownerID = session.corpid
            else:
                sectionName = localization.GetByLabel('UI/PeopleAndPlaces/PersonalLocations')
                self.ownerID = session.charid
            uicontrols.EveLabelMedium(text=sectionName, parent=sectionContainer, align=uiconst.TOALL, width=60)
        else:
            ownerID = settings.char.ui.Get('bookmarkFolderDefaultOwner', session.charid)
            self.sectionCombo = uicontrols.Combo(name='sectionCombo', parent=sectionContainer, align=uiconst.TOALL, width=0, select=ownerID, options=[(localization.GetByLabel('UI/PeopleAndPlaces/PersonalLocations'), session.charid), (localization.GetByLabel('UI/PeopleAndPlaces/CorporationLocations'), session.corpid)])
        buttons = self.GetButtons()
        buttonGroup = uicontrols.ButtonGroup(name='buttonGroup', parent=main, btns=buttons)
        submitButton = buttonGroup.GetBtnByIdx(0)
        submitButton.OnSetFocus()

    def GetButtons(self):
        return [(localization.GetByLabel('UI/Common/Submit'), self.Confirm, []), (localization.GetByLabel('UI/Common/Cancel'), self.Cancel, [])]

    def Confirm(self, *args):
        name = self.nameEdit.GetValue()
        if name.strip() == '':
            raise UserError('CustomInfo', {'info': localization.GetByLabel('UI/Map/MapPallet/msgPleaseTypeSomething')})
        if self.ownerID is None:
            self.ownerID = self.sectionCombo.GetValue()
        if self.isNew:
            sm.GetService('bookmarkSvc').CreateFolder(self.ownerID, name)
        else:
            sm.GetService('bookmarkSvc').UpdateFolder(self.ownerID, self.folder.folderID, name)
        settings.char.ui.Set('bookmarkFolderDefaultOwner', self.ownerID)
        self.Close()

    def Cancel(self, *args):
        self.Close()
