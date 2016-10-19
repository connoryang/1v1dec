#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\control\eveSinglelineEdit.py
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.control.singlelineedit import SinglelineEditCore
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveWindowUnderlay import BumpedUnderlay
import carbonui.const as uiconst
from eve.client.script.ui.control.tooltips import TooltipGeneric
from eve.client.script.ui.util.linkUtil import GetItemIDFromTextLink, GetCharIDFromTextLink
import evetypes
import localization
import util
import uiutil
import trinity

class SinglelineEdit(SinglelineEditCore):
    __guid__ = 'uicontrols.SinglelineEdit'
    default_left = 0
    default_top = 2
    default_width = 80
    default_height = 18
    default_align = uiconst.TOPLEFT
    capsWarning = None
    capsLockUpdateThread = None

    def ApplyAttributes(self, attributes):
        SinglelineEditCore.ApplyAttributes(self, attributes)
        self.displayHistory = True
        if self.GetAlign() == uiconst.TOALL:
            self.height = 0
        else:
            self.height = self.default_height
        self.isTypeField = attributes.isTypeField
        self.isCharacterField = attributes.isCharacterField
        self.isCharCorpOrAllianceField = attributes.isCharCorpOrAllianceField
        self.isLocationField = attributes.isLocationField

    def Close(self):
        if self.capsWarning:
            self.capsWarning.Close()
        self.capsLockUpdateThread = None
        SinglelineEditCore.Close(self)

    def SetPasswordChar(self, char):
        SinglelineEditCore.SetPasswordChar(self, char)
        if self.passwordchar:
            self.capsWarning = TooltipGeneric(parent=uicore.layer.hint, idx=0, opacity=0.0)
            self.capsWarning.defaultPointer = uiconst.POINT_LEFT_2
            self.capsLockUpdateThread = AutoTimer(300, self.UpdateCapsState)
        else:
            self.capsLockUpdateThread = None

    def Prepare_(self):
        self.sr.text = Label(name='edittext', parent=self._textClipper, left=self.TEXTLEFTMARGIN, state=uiconst.UI_DISABLED, maxLines=1, align=uiconst.CENTERLEFT, fontsize=self.fontsize)
        self.sr.hinttext = Label(parent=self._textClipper, name='hinttext', align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, maxLines=1, left=self.TEXTLEFTMARGIN, fontsize=self.fontsize)
        self.sr.background = BumpedUnderlay(bgParent=self, showFill=True)

    def SetLabel(self, text):
        self.sr.label = EveLabelSmall(parent=self, name='__caption', text=text, state=uiconst.UI_DISABLED, align=uiconst.TOPLEFT, idx=0)
        self.sr.label.top = -self.sr.label.textheight
        if self.adjustWidth:
            self.width = max(self.width, self.sr.label.textwidth)

    def OnDropData(self, dragObj, nodes):
        SinglelineEditCore.OnDropData(self, dragObj, nodes)
        if self.isTypeField:
            self.OnDropType(dragObj, nodes)
        elif self.isLocationField:
            self.OnDropLocation(dragObj, nodes)
        if self.isCharCorpOrAllianceField:
            self.OndDropCharCorpOrAlliance(dragObj, nodes)
        elif self.isCharacterField:
            self.OnDropCharacter(dragObj, nodes)

    def OnDropType(self, dragObj, nodes):
        node = nodes[0]
        guid = node.Get('__guid__', None)
        typeID = None
        if guid in ('xtriui.ShipUIModule', 'xtriui.InvItem', 'listentry.InvItem', 'listentry.InvAssetItem'):
            typeID = getattr(node.item, 'typeID', None)
        elif guid in ('listentry.GenericMarketItem', 'listentry.QuickbarItem'):
            typeID = getattr(node, 'typeID', None)
        if typeID:
            typeName = evetypes.GetName(typeID)
            self.SetValueAfterDragging(typeName, draggedValue=typeID)

    def OnDropLocation(self, dragObj, nodes):
        node = nodes[0]
        guid = node.Get('__guid__', None)
        locationItemID = None
        itemID = GetItemIDFromTextLink(node, None)
        if self._IsLocation(itemID):
            locationItemID = itemID
        elif guid in ('xtriui.ListSurroundingsBtn', 'listentry.LocationTextEntry', 'listentry.LabelLocationTextTop', 'listentry.LocationGroup', 'listentry.LocationSearchItem'):
            if self._IsLocation(node.itemID):
                locationItemID = node.itemID
        if locationItemID:
            self.SetValueAfterDragging(cfg.evelocations.Get(locationItemID).name, locationItemID)

    def _IsLocation(self, itemID):
        if not itemID:
            return False
        try:
            cfg.evelocations.Get(itemID)
            return True
        except KeyError:
            return False

    def OnDropCharacter(self, dragObj, nodes):
        charInfo = GetDroppedCharInfo(nodes[0])
        if charInfo is not None:
            self.SetValueAfterDragging(charInfo.charName, charInfo.charID)

    def OndDropCharCorpOrAlliance(self, dragObj, nodes):
        itemInfo = GetDroppedCharCorpOrAllianceName(nodes[0])
        if itemInfo is not None:
            self.SetValueAfterDragging(itemInfo.itemName, itemID=itemInfo.itemID)

    def SetValueAfterDragging(self, name, draggedValue):
        self.SetValue(name)
        self.draggedValue = draggedValue

    def UpdateCapsState(self):
        if not self.capsWarning or self.capsWarning.destroyed or self.destroyed:
            self.capsLockUpdateThread = None
            return
        if self.passwordchar is not None:
            if trinity.app.GetKeyState(uiconst.VK_CAPITAL) == True and self is uicore.registry.GetFocus():
                if self.capsWarning:
                    if self.capsWarning.opacity == 0.0:
                        self.capsWarning.opacity = 1.0
                    self.capsWarning.display = True
                    self.capsWarning.SetTooltipString(localization.GetByLabel('/Carbon/UI/Common/CapsLockWarning'), self)
            else:
                self.capsWarning.display = False


class PrefixedSingleLineEdit(SinglelineEdit):
    __guid__ = 'uicontrols.PrefixedSingleLineEdit'

    def ApplyAttributes(self, attributes):
        self.prefix = attributes.prefix or ''
        setvalue = attributes.setvalue or ''
        if not setvalue:
            setvalue = self.prefix
        elif setvalue and not setvalue.startswith(self.prefix):
            setvalue = self.prefix + setvalue
        attributes.setvalue = setvalue
        SinglelineEdit.ApplyAttributes(self, attributes)
        self._OnChange = self.OnChange
        self.OnChange = self.OnNameEditEdited
        self.SetHistoryVisibility(False)
        self.RefreshCaretPosition()

    def OnNameEditEdited(self, *args):
        args2 = list(args)
        newText = args[0]
        caretpos = self.caretIndex[0]
        if caretpos < len(self.prefix):
            text = self.prefix
            if len(newText) > caretpos:
                text += newText[caretpos:].lstrip()
            newText = text
            self.SetText(newText)
            self.caretIndex = self.GetCursorFromIndex(len(self.prefix))
            self.RefreshCaretPosition()
            args2[0] = newText
        if self._OnChange:
            self._OnChange(*args2)

    def GetSelectionBounds(self):
        selFrom, selTo = super(PrefixedSingleLineEdit, self).GetSelectionBounds()
        if selFrom and selFrom[0] < len(self.prefix):
            newFrom = len(self.prefix)
            selFrom = (newFrom, self.sr.text.GetWidthToIndex(newFrom)[1])
            newTo = max(newFrom, selTo[0])
            selTo = (newTo, self.sr.text.GetWidthToIndex(newTo)[1])
        if getattr(self, 'prefix', None) and self.caretIndex[0] < len(self.prefix):
            self.caretIndex = self.GetCursorFromIndex(len(self.prefix))
            self.RefreshCaretPosition()
        return (selFrom, selTo)


from carbonui.control.singlelineedit import SinglelineEditCoreOverride
SinglelineEditCoreOverride.__bases__ = (SinglelineEdit,)

def GetDroppedCharCorpOrAllianceName(node):
    if not IsUserNode(node):
        return
    validTypeIDs = const.characterTypeByBloodline.values() + [const.typeCorporation, const.typeAlliance]
    itemID = GetItemIDFromTextLink(node, validTypeIDs)
    if itemID is None:
        itemID = node.itemID
    if util.IsCharacter(itemID) or util.IsCorporation(itemID) or util.IsAlliance(itemID):
        itemName = cfg.eveowners.Get(itemID).name
        return util.KeyVal(itemName=itemName, itemID=itemID)


def GetDroppedCharInfo(node):
    if not IsUserNode(node):
        return
    charID = GetCharIDFromTextLink(node)
    if charID is None:
        charID = node.charID
    if util.IsCharacter(charID):
        charName = cfg.eveowners.Get(charID).name
        return util.KeyVal(charName=charName, charID=charID)


def IsUserNode(node):
    isUserNode = node.Get('__guid__', None) in uiutil.AllUserEntries() + ['TextLink']
    return isUserNode
