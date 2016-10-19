#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\redeemsvc.py
import evetypes
import service
from eve.client.script.ui.control import entries as listentry
import uiprimitives
import uicontrols
import util
import uiutil
import carbonui.const as uiconst
import localization
import log
import blue
import uthread
from eve.common.script.util.notificationconst import notificationTypeNewRedeemableItem
from notifications.common.notification import Notification

class RedeemService(service.Service):
    __guid__ = 'svc.redeem'
    __notifyevents__ = ['OnRedeemingQueueUpdated', 'OnSessionChanged']

    def __init__(self):
        service.Service.__init__(self)
        self.tokens = None

    def Run(self, *args):
        service.Service.Run(self, *args)
        self.GetRedeemTokens()

    def GetRedeemTokens(self, force = False):
        if self.tokens is None or force:
            self.tokens = sm.RemoteSvc('userSvc').GetRedeemTokens()
        return self.tokens

    def ReverseRedeem(self, item):
        if eve.Message('ConfirmReverseRedeem', {'type': (const.UE_TYPEID, item.typeID),
         'quantity': item.stacksize}, uiconst.YESNO) != uiconst.ID_YES:
            return
        try:
            sm.RemoteSvc('userSvc').ReverseRedeem(item.itemID)
        finally:
            self.OnRedeemingQueueUpdated()

    def ToggleRedeemWindow(self):
        RedeemWindow.ToggleOpenClose(charID=session.charid, stationID=session.stationid or session.structureid)

    def OpenRedeemWindow(self):
        wnd = RedeemWindow.GetIfOpen()
        if wnd is None:
            wnd = RedeemWindow.Open(charID=session.charid, stationID=session.stationid or session.structureid, useDefaultPos=True)
            wnd.left -= 160
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()

    def CloseRedeemWindow(self):
        RedeemWindow.CloseIfOpen()

    def ClaimRedeemTokens(self, tokens, charID):
        try:
            sm.RemoteSvc('userSvc').ClaimRedeemTokens(tokens, charID)
        except UserError as e:
            eve.Message(e.msg, e.dict)
            if e.msg == 'RedeemTokenClaimed2':
                eve.Message('RedeemTokenClaimed2', e.dict)
                tokensRedeemed = e.dict['tokensRedeemed']
                sm.ScatterEvent('OnTokensRedeemed', tokensRedeemed, charID)
        except (Exception,) as e:
            raise

        self.OnRedeemingQueueUpdated()

    def RedeemAndActivateType(self, typeID):
        sm.RemoteSvc('userSvc').RedeemAndActivateType(typeID)

    def OnRedeemingQueueUpdated(self):
        oldTokens = self.tokens
        currentTokens = self._UpdateTokensAndNotify()
        newTokens = self._FindNewTokens(oldTokens, currentTokens)
        self._BroadcastRedeemingNotification(newTokens)

    def _UpdateTokensAndNotify(self):
        tokens = self.GetRedeemTokens(force=True)
        sm.ScatterEvent('OnRedeemingTokensUpdated')
        return tokens

    def _FindNewTokens(self, oldTokens, currentTokens):
        oldTokensById = {(t.tokenID, t.massTokenID):t for t in oldTokens}
        newTokens = []
        for token in currentTokens:
            key = (token.tokenID, token.massTokenID)
            if key not in oldTokensById:
                newTokens.append(token)

        return newTokens

    def _BroadcastRedeemingNotification(self, newTokens):
        if len(newTokens) == 0:
            return
        created = blue.os.GetWallclockTime()
        notification = RedeemingNotification(tokens=newTokens, created=created)
        sm.ScatterEvent('OnNewNotificationReceived', notification)

    def OnSessionChanged(self, *args):
        self.CloseRedeemWindow()


class RedeemWindow(uicontrols.Window):
    __guid__ = 'form.RedeemWindow'
    default_windowID = 'redeem'
    default_iconNum = 'res:/ui/Texture/WindowIcons/redeem.png'
    __notifyevents__ = ['OnRedeemingTokensUpdated']

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        self.stationID = attributes.stationID
        self.charID = attributes.charID
        self.selectedTokens = {}
        self.SetCaption(localization.GetByLabel('UI/RedeemWindow/RedeemItem'))
        self.SetMinSize([640, 260])
        self.SetWndIcon(self.iconNum)
        self.NoSeeThrough()
        self.SetScope('all')
        self.uiSvc = sm.StartService('ui')
        h = self.sr.topParent.height - 2
        self.sr.picParent = uiprimitives.Container(name='picpar', parent=self.sr.topParent, align=uiconst.TORIGHT, width=h, height=h, left=const.defaultPadding, top=const.defaultPadding)
        self.sr.pic = uiprimitives.Sprite(parent=self.sr.picParent, align=uiconst.RELATIVE, left=1, top=3, height=h, width=h)
        sm.GetService('photo').GetPortrait(self.charID, 64, self.sr.pic)
        self.state = uiconst.UI_NORMAL
        self.sr.windowCaption = uicontrols.WndCaptionLabel(text=localization.GetByLabel('UI/RedeemWindow/RedeemItem'), parent=self.sr.topParent, align=uiconst.RELATIVE)
        tp = 5
        self.redeemingAmountLabel = uicontrols.EveLabelMedium(text=self.GetTextForRedeemingAmountLabel(0), parent=self.sr.topParent, top=tp, left=60, state=uiconst.UI_DISABLED, align=uiconst.TOPRIGHT)
        tp += self.redeemingAmountLabel.textheight
        if self.stationID:
            self.solarsystemID = session.solarsystemid2
            text = localization.GetByLabel('UI/RedeemWindow/ItemsDeliveryLocation', solarSystem=cfg.evelocations.Get(self.solarsystemID))
            self.redeemToLabel = uicontrols.EveLabelMedium(text=text, parent=self.sr.topParent, top=tp, left=60, state=uiconst.UI_DISABLED, align=uiconst.TOPRIGHT)
        else:
            text = localization.GetByLabel('UI/RedeemWindow/IncorrectPlayerLocation')
            uicontrols.EveLabelMedium(text=text, parent=self.sr.topParent, top=tp, left=60, state=uiconst.UI_DISABLED, align=uiconst.TOPRIGHT)
        uiprimitives.Container(name='push', parent=self.sr.main, align=uiconst.TOLEFT, width=const.defaultPadding)
        uiprimitives.Container(name='push', parent=self.sr.main, align=uiconst.TORIGHT, width=const.defaultPadding)
        btns = [(localization.GetByLabel('UI/RedeemWindow/RedeemSelectedItems'),
          self.RedeemSelected,
          (),
          84)]
        self.sr.redeemBtn = uicontrols.ButtonGroup(btns=btns, parent=self.sr.main, unisize=1)
        self.sr.itemsScroll = uicontrols.Scroll(parent=self.sr.main, padTop=const.defaultPadding)
        self.sr.itemsScroll.hiliteSorted = 0
        uiprimitives.Container(name='push', parent=self.sr.main, align=uiconst.TOBOTTOM, width=6)
        uthread.new(self.UpdateRedeemingWindowContent)
        return self

    def GetTextForRedeemingAmountLabel(self, tokenCount):
        return localization.GetByLabel('UI/RedeemWindow/ReedemNumItems', num=tokenCount, player=self.charID)

    def UpdateRedeemingAmountLabel(self):
        self.redeemingAmountLabel.text = self.GetTextForRedeemingAmountLabel(len(self.tokens))

    def UpdateRedeemingWindowContent(self):
        self.tokens = sm.GetService('redeem').GetRedeemTokens()
        self.UpdateRedeemingAmountLabel()
        listItemContainsExpiryDate = len([ token for token in self.tokens if token.expireDateTime ]) > 0
        self.UpdateRedeemingScrollList([ self.ProcessToken(token) for token in self.tokens ], listItemContainsExpiryDate)
        self.UpdateDeliveryLocation()

    def UpdateRedeemingScrollList(self, scrollList, listItemContainsExpiryDate):
        if self.sr.itemsScroll is not None:
            self.sr.itemsScroll.sr.id = 'itemsScroll'
            self.sr.itemsScroll.sr.lastSelected = None
            self.sr.itemsScroll.sr.minColumnWidth = {localization.GetByLabel('UI/Common/Type'): 50}
            headers = [localization.GetByLabel('UI/Common/Type'), localization.GetByLabel('UI/Common/Quantity'), localization.GetByLabel('UI/Common/Description')]
            if listItemContainsExpiryDate == 1:
                headers.append(localization.GetByLabel('UI/Common/Expires'))
                dWidth, dHeight = uicontrols.EveLabelMedium.MeasureTextSize(util.FmtDate(blue.os.GetWallclockTime(), 'ln'))
                self.sr.itemsScroll.sr.fixedColumns = {localization.GetByLabel('UI/Common/Expires'): dWidth + 16}
            self.sr.itemsScroll.Load(contentList=scrollList, headers=headers)

    def ProcessToken(self, token):
        description = token.description or (localization.GetByLabel(token.label) if token.label else '')
        quantity = token.quantity
        if not evetypes.Exists(token.typeID):
            msg = localization.GetByLabel('UI/RedeemWindow/UnknownType') + '<t>%d<t>%s' % (quantity, description)
            log.LogWarn("A Token was found that we don't know about", token.typeID, 'ignoring it for now! Coming Soon(tm)')
            return listentry.Get('Generic', {'label': msg})
        if token.expireDateTime:
            description = '%s<t>%s' % (description, localization.GetByLabel('UI/RedeemWindow/RedeemExpires', expires=token.expireDateTime).replace('<br>', ''))
        if token.stationID:
            description = localization.GetByLabel('UI/RedeemWindow/RedeemableTo', desc=description, station=token.stationID)
            selectedTokenDeliveryLocation = token.stationID
        else:
            selectedTokenDeliveryLocation = self.stationID
        self.selectedTokens[token.tokenID, token.massTokenID] = selectedTokenDeliveryLocation
        quantity *= evetypes.GetPortionSize(token.typeID)
        label = '%s<t>%s<t>%s' % (evetypes.GetName(token.typeID), quantity, description)
        return listentry.Get('RedeemToken', {'itemID': None,
         'tokenID': token.tokenID,
         'massTokenID': token.massTokenID,
         'info': token,
         'typeID': token.typeID,
         'stationID': selectedTokenDeliveryLocation,
         'label': label,
         'quantity': quantity,
         'getIcon': 1,
         'retval': (token.tokenID, token.massTokenID, selectedTokenDeliveryLocation),
         'OnChange': self.OnTokenChange,
         'checked': True})

    def OnRedeemingTokensUpdated(self):
        self.UpdateRedeemingWindowContent()

    def RedeemSelected(self, *args):
        if self.stationID is None:
            raise UserError('RedeemOnlyInStation')
        if not len(self.selectedTokens.keys()):
            return
        if self.IsMultipleStations():
            stations = ''
            for stationID in set(self.selectedTokens.values()):
                stations += '%s<br>' % cfg.evelocations.Get(stationID).name

            if eve.Message('RedeemConfirmClaimMultiple', {'char': self.charID,
             'stations': stations}, uiconst.YESNO, default=uiconst.ID_NO) != uiconst.ID_YES:
                return
        else:
            redeemStation = self.selectedTokens.values()[0]
            if eve.Message('RedeemConfirmClaim', {'char': self.charID,
             'station': redeemStation}, uiconst.YESNO, default=uiconst.ID_NO) != uiconst.ID_YES:
                return
        sm.StartService('redeem').ClaimRedeemTokens(self.selectedTokens.keys(), self.charID)
        self.Close()

    def OnTokenChange(self, checkbox, *args):
        tokenID, massTokenID, stationID = checkbox.data['retval']
        k = (tokenID, massTokenID)
        gv = True
        try:
            gv = checkbox.GetValue()
        except:
            pass

        if gv:
            self.selectedTokens[k] = stationID
        elif k in self.selectedTokens:
            del self.selectedTokens[k]
        self.UpdateDeliveryLocation()

    def UpdateDeliveryLocation(self):
        text = ''
        if len(self.selectedTokens) > 0:
            self.sr.redeemBtn.state = uiconst.UI_NORMAL
            if self.IsMultipleStations():
                text = localization.GetByLabel('UI/RedeemWindow/ItemsDeliveryMultiple')
            else:
                redeemLocationID = self.selectedTokens.values()[0]
                if util.IsStation(redeemLocationID):
                    text = localization.GetByLabel('UI/RedeemWindow/ItemsDeliveryLocation', solarSystem=cfg.evelocations.Get(self.uiSvc.GetStation(redeemLocationID).solarSystemID))
                elif redeemLocationID is not None:
                    try:
                        solarsystemID = sm.GetService('structureDirectory').GetStructures()[redeemLocationID]['solarSystemID']
                    except KeyError:
                        solarsystemID = self.solarsystemID if self.solarsystemID is not None else session.solarsystemid2

                    text = localization.GetByLabel('UI/RedeemWindow/ItemsDeliveryLocation', solarSystem=cfg.evelocations.Get(solarsystemID))
        elif self.stationID is not None:
            text = localization.GetByLabel('UI/RedeemWindow/ItemsDeliveryLocation', solarSystem=cfg.evelocations.Get(self.solarsystemID))
        if len(self.selectedTokens) == 0:
            self.sr.redeemBtn.state = uiconst.UI_DISABLED
        if hasattr(self, 'redeemToLabel'):
            self.redeemToLabel.text = text

    def IsMultipleStations(self):
        return len(set(self.selectedTokens.values())) > 1


class RedeemToken(listentry.Item):
    __guid__ = 'listentry.RedeemToken'
    isDropLocation = False

    def ApplyAttributes(self, attributes):
        listentry.Item.ApplyAttributes(self, attributes)
        self.sr.overlay = uiprimitives.Container(name='overlay', align=uiconst.TOPLEFT, parent=self, height=1)
        self.sr.tlicon = None

    def Startup(self, *args):
        listentry.Item.Startup(self, args)
        cbox = uicontrols.Checkbox(text='', parent=self, configName='cb', retval=None, checked=1, align=uiconst.TOPLEFT, pos=(6, 4, 0, 0), callback=self.CheckBoxChange)
        cbox.data = {}
        self.sr.checkbox = cbox
        self.sr.checkbox.state = uiconst.UI_NORMAL

    def Load(self, args):
        listentry.Item.Load(self, args)
        data = self.sr.node
        self.sr.checkbox.SetGroup(data.group)
        self.sr.checkbox.SetChecked(data.checked, 0)
        self.sr.checkbox.data = {'key': (data.tokenID, data.massTokenID),
         'retval': data.retval}
        self.sr.icon.left = 24
        self.sr.label.left = self.sr.icon.left + self.sr.icon.width + 4
        if self.sr.techIcon:
            self.sr.techIcon.left = 24
        gdm = sm.StartService('godma').GetType(self.sr.node.info.typeID)
        if self.sr.tlicon and gdm.techLevel not in (2, 3):
            self.sr.tlicon.state = uiconst.UI_HIDDEN

    def OnClick(self, *args):
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        lastSelected = self.sr.node.scroll.sr.lastSelected
        if lastSelected is None:
            shift = 0
        idx = self.sr.node.idx
        if self.sr.checkbox.checked:
            eve.Message('DiodeDeselect')
        else:
            eve.Message('DiodeClick')
        isIt = not self.sr.checkbox.checked
        self.sr.checkbox.SetChecked(isIt)
        self.sr.node.scroll.sr.lastSelected = idx

    def GetMenu(self):
        return [(uiutil.MenuLabel('UI/Commands/ShowInfo'), self.ShowInfo, (self.sr.node,))]

    def CheckBoxChange(self, *args):
        self.sr.node.checked = self.sr.checkbox.checked
        self.sr.node.OnChange(*args)


class RedeemingNotification(Notification):

    def __init__(self, tokens, created = None):
        created = created or blue.os.GetWallclockTime()
        super(RedeemingNotification, self).__init__(notificationID=-1, typeID=notificationTypeNewRedeemableItem, senderID=None, receiverID=None, processed=False, created=created, data=None)
        numTokens = len(tokens)
        self.subject = localization.GetByLabel('UI/RedeemWindow/NewRedeemableItemsNotification', quantity=numTokens)
        if numTokens == 1:
            token = tokens[0]
            quantity = token.quantity * evetypes.GetPortionSize(token.typeID)
            self.subtext = localization.GetByLabel('UI/Contracts/ContractsWindow/TypeNameWithQuantity', typeID=token.typeID, quantity=quantity)

    def Activate(self):
        sm.GetService('redeem').OpenRedeemWindow()
