#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\notifications\client\controls\notificationEntry.py
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.shared.stateFlag import AddAndSetFlagIconFromData
import localization
import blue
import carbon.common.script.util.format as formatUtil
import carbonui.const as uiconst
import eve.common.script.util.notificationconst as notificationConst
import math
from notifications.client.controls.notificationTextures import NOTIFICATION_TYPE_TO_TEXTURE
from notifications.common.formatters.killMailBase import KillMailBaseFormatter
from notifications.common.formatters.killMailFinalBlow import KillMailFinalBlowFormatter
import eve.client.script.ui.util.uix as uiUtils
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.control.eveIcon import Icon
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from utillib import KeyVal
from eve.client.script.ui.control.eveIcon import GetLogoIcon
MAINAREA_WIDTH = 224
LEFT_PANEL_WIDTH = 40
MINENTRYHEIGHT = 50
TITLE_PADDING = (0, 5, 0, 0)
SUBTEXT_PADDING = (0, 0, 0, 0)
TIMETEXT_PADDING = (0, 5, 0, 5)
LEFT_PANEL_PADDING = (5, 5, 10, 5)
TIMETEXT_PLACEHOLDER = '123'
TIMETEXT_COLOR = (0.5, 0.5, 0.5)
CHAR_PORTRAIT_SIZE = 128
SHIP_TYPE_ICON_SIZE = 40
SHIP_TECH_ICON_SIZE = 16
FLAG_ICON_PADDING = 10
CORP_LOGO_SIZE = 40
NOTIFICATION_SPRITE_SIZE = 40
HISTORY_READ_UP_TEXTURE_PATH = 'res:/UI/Texture/classes/Notifications/historyBackReadUp.png'
HISTORY_READ_OVER_TEXTURE_PATH = 'res:/UI/Texture/classes/Notifications/historyBackReadOver.png'
DEFAULT_NOTIFICATION_TEXTURE_PATH = 'res:/ui/Texture/WindowIcons/bountyoffice.png'
NOTIFICATION_ICONS_TEXTURE_PATH = 'res:/UI/Texture/Icons/notifications/notificationIcon_%s.png'
BLINK_SPRITE_TEXTURE_PATH = 'res:/UI/Texture/classes/Neocom/buttonBlink.png'
BLINK_SPRITE_ROTATION = math.pi * 0.75
BLINK_SPRITE_DURATION = 0.8
BLINK_SPRITE_LOOPS = 1
TIME_AGO_LABEL = 'Notifications/NotificationWidget/NotificationTimeAgo'
MAIN_BACKGROUND_CORNER_SIZE = 6
MAIN_BACKGROUND_OFFSET = -5

class NotificationEntry(Container):
    default_height = MINENTRYHEIGHT
    default_state = uiconst.UI_NORMAL
    notification = None
    contentLoaded = False
    blinkSprite = None
    titleLabel = None
    subtextLabel = None
    timeLabel = None

    def GetFormattedTimeString(self, timestamp):
        delta = blue.os.GetWallclockTime() - timestamp
        return formatUtil.FmtTimeIntervalMaxParts(delta, breakAt='second', maxParts=2)

    def UpdateNotificationEntryHeight(self):
        pl, pt, pr, pb = TITLE_PADDING
        size = EveLabelMedium.MeasureTextSize(self.title, width=MAINAREA_WIDTH - pl - pr, bold=True)
        height = size[1] + pt + pb
        if self.subtext:
            pl, pt, pr, pb = SUBTEXT_PADDING
            size = EveLabelMedium.MeasureTextSize(self.subtext, width=MAINAREA_WIDTH - pl - pr)
            height += size[1] + pt + pb
        if self.created:
            pl, pt, pr, pb = TIMETEXT_PADDING
            size = EveLabelSmall.MeasureTextSize(TIMETEXT_PLACEHOLDER, width=MAINAREA_WIDTH - pl - pr)
            height += size[1] + pt + pb
        return max(MINENTRYHEIGHT, height)

    def ApplyAttributes(self, attributes):
        self.notification = attributes.notification
        self.developerMode = attributes.developerMode
        self.created = attributes.created
        self.title = self.notification.subject
        self.subtext = self.notification.subtext
        attributes.height = self.UpdateNotificationEntryHeight()
        Container.ApplyAttributes(self, attributes)

    def LoadContent(self):
        if self.contentLoaded:
            return
        self.contentLoaded = True
        self._CreateMainBackground()
        self._CreatePanels()
        self._CreateNotificationText()
        self._CreateNotificationImage()
        if self.created:
            timeinterval = max(blue.os.GetWallclockTime() - self.created, 0)
            createdText = localization.GetByLabel(TIME_AGO_LABEL, time=timeinterval)
            self.timeLabel = EveLabelSmall(name='timeLabel', parent=self.rightContainer, align=uiconst.TOTOP, color=TIMETEXT_COLOR, padding=TIMETEXT_PADDING)
            self.timeLabel.text = createdText
        notification = self.notification
        if notification.typeID in [notificationConst.notificationTypeKillReportFinalBlow, notificationConst.notificationTypeKillReportVictim]:
            shipTypeID = KillMailFinalBlowFormatter.GetVictimShipTypeID(notification.data)
            if shipTypeID is not None:
                parentContainer = self.leftContainer
                Icon(name='shipTypeIcon', parent=parentContainer, align=uiconst.TOPRIGHT, size=SHIP_TYPE_ICON_SIZE, typeID=shipTypeID)
                shipTechIcon = Sprite(name='shipTechIcon', parent=parentContainer, width=SHIP_TECH_ICON_SIZE, height=SHIP_TECH_ICON_SIZE, idx=0)
                uiUtils.GetTechLevelIcon(shipTechIcon, 0, shipTypeID)
                self.imageSprite.GetDragData = lambda *args: self.MakeKillDragObject(notification)
        if self.ShouldDisplayPortrait(notification):
            item = cfg.eveowners.Get(notification.senderID)
            if item.IsCharacter():
                sm.GetService('photo').GetPortrait(notification.senderID, CHAR_PORTRAIT_SIZE, self.characterSprite)
                if notification.typeID in notificationConst.notificationShowStanding:
                    charinfo = item
                    self.imageSprite.GetMenu = lambda : sm.GetService('menu').GetMenuFormItemIDTypeID(notification.senderID, charinfo.typeID)
                    self.imageSprite.GetDragData = lambda *args: self.MakeCharacterDragObject(notification.senderID)
                    charData = KeyVal()
                    charData.charID = notification.senderID
                    charData.charinfo = charinfo
                    AddAndSetFlagIconFromData(charData, parentCont=self.leftContainer, top=self.characterSprite.height - FLAG_ICON_PADDING)
            else:
                self.corpLogo = GetLogoIcon(itemID=notification.senderID, parent=self.leftContainer, align=uiconst.TOPLEFT, size=CORP_LOGO_SIZE, state=uiconst.UI_DISABLED, ignoreSize=True)
            self.characterSprite.state = uiconst.UI_NORMAL

    def _CreateMainBackground(self):
        self.filler = Frame(name='mainBackgroundFrame', bgParent=self, texturePath=HISTORY_READ_UP_TEXTURE_PATH, cornerSize=MAIN_BACKGROUND_CORNER_SIZE, offset=MAIN_BACKGROUND_OFFSET)

    def _CreatePanels(self):
        self.leftContainer = Container(name='leftContainer-notificationGraphic', width=LEFT_PANEL_WIDTH, padding=LEFT_PANEL_PADDING, parent=self, align=uiconst.TOLEFT)
        self.rightContainer = ContainerAutoSize(name='rightContainer-notificationInfo', width=MAINAREA_WIDTH, parent=self, align=uiconst.TOLEFT)

    def _CreateNotificationText(self):
        self.titleLabel = EveLabelMedium(name='notificationSubjectLabel', parent=self.rightContainer, align=uiconst.TOTOP, text=self.title, padding=TITLE_PADDING, bold=True)
        if self.subtext:
            self.subtextLabel = EveLabelMedium(name='notificationSubtextLabel', parent=self.rightContainer, align=uiconst.TOTOP, text=self.subtext, padding=SUBTEXT_PADDING)

    def _CreateNotificationImage(self):
        if self.notification:
            texture = self.GetTexturePathForNotification(self.notification.typeID)
        else:
            texture = DEFAULT_NOTIFICATION_TEXTURE_PATH
        self.imageSprite = Sprite(name='notificationSprite', parent=self.leftContainer, texturePath=texture, align=uiconst.TOPLEFT, width=NOTIFICATION_SPRITE_SIZE, height=NOTIFICATION_SPRITE_SIZE)
        self.characterSprite = Sprite(name='notificationCharacterSprite', parent=self.leftContainer, texturePath=texture, align=uiconst.TOPLEFT, width=NOTIFICATION_SPRITE_SIZE, height=NOTIFICATION_SPRITE_SIZE, state=uiconst.UI_HIDDEN)

    def BlinkFinished(self, *args):
        if self.blinkSprite and not self.blinkSprite.destroyed:
            self.blinkSprite.Close()
            self.blinkSprite = None

    def Blink(self):
        if self.blinkSprite is None:
            self.blinkSprite = Sprite(bgParent=self, name='blinkSprite', texturePath=BLINK_SPRITE_TEXTURE_PATH, idx=0)
        self.blinkSprite.Show()
        uicore.animations.SpSwoopBlink(self.blinkSprite, rotation=BLINK_SPRITE_ROTATION, duration=BLINK_SPRITE_DURATION, loops=BLINK_SPRITE_LOOPS, callback=self.BlinkFinished)

    def GetTexturePathForNotification(self, notificationTypeID):
        texture = NOTIFICATION_TYPE_TO_TEXTURE.get(notificationTypeID, '')
        if not texture or not blue.paths.exists(texture):
            texture = None
        return texture

    def ShouldDisplayPortrait(self, notification):
        if notification and notification.typeID in notificationConst.notificationDisplaySender:
            return True
        else:
            return False

    def GetHint(self):
        if self.notification and self.developerMode:
            return '%s %s %s %s' % (str(self.notification.typeID),
             str(self.notification.subject),
             str(self.notification.senderID),
             self.notification.body)
        else:
            return ''

    def MakeCharacterDragObject(self, charid):
        typeID = cfg.eveowners.Get(charid).typeID
        fakeNode = KeyVal()
        fakeNode.charID = charid
        fakeNode.info = cfg.eveowners.Get(charid)
        fakeNode.itemID = charid
        fakeNode.__guid__ = 'listentry.User'
        return [fakeNode]

    def MakeKillDragObject(self, notification):
        fakeNode = KeyVal()
        kmID, kmHash = KillMailBaseFormatter.GetKillMailIDandHash(notification.data)
        theRealKm = sm.RemoteSvc('warStatisticMgr').GetKillMail(kmID, kmHash)
        fakeNode.mail = theRealKm
        fakeNode.__guid__ = 'listentry.KillMail'
        return [fakeNode]

    def OnMouseEnter(self, *args):
        self.filler.texturePath = HISTORY_READ_OVER_TEXTURE_PATH

    def OnMouseExit(self, *args):
        self.filler.texturePath = HISTORY_READ_UP_TEXTURE_PATH
