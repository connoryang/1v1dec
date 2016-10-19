#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\charsheet\securityStatusPanel.py
from carbon.common.script.util.format import FmtDate
from carbonui.primitives.container import Container
from eve.client.script.ui.control import entries
from eve.client.script.ui.control.eveScroll import Scroll
from eve.common.script.mgt import appLogConst as logConst
import localization
from localization import GetByLabel

class SecurityStatusPanel(Container):
    default_name = 'SecurityStatusPanel'
    __notifyevents__ = []

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.scroll = Scroll(parent=self, padding=(0, 4, 0, 4))
        self.scroll.sr.id = 'charsheet_securitystatus'

    def LoadPanel(self, *args):
        crimewatchSvc = sm.GetService('crimewatchSvc')
        data = crimewatchSvc.GetSecurityStatusTransactions()
        self.scroll.Clear()
        scrolllist = []
        for transaction in data:
            if transaction.eventTypeID == logConst.eventSecStatusGmModification:
                subject = GetByLabel('UI/Generic/FormatStandingTransactions/subjectSetBySlashCmd')
                body = GetByLabel('UI/Generic/FormatStandingTransactions/messageResetBySlashCmd')
            elif transaction.eventTypeID == logConst.eventSecStatusGmRollback:
                subject = GetByLabel('UI/Generic/FormatStandingTransactions/subjectSetBySlashCmd')
                body = GetByLabel('UI/Generic/FormatStandingTransactions/messageResetBySlashCmd')
            elif transaction.eventTypeID == logConst.eventSecStatusIllegalAggression:
                cfg.eveowners.Prime([transaction.otherOwnerID])
                cfg.evelocations.Prime([transaction.locationID])
                subject = GetByLabel('UI/Generic/FormatStandingTransactions/subjectCombatAgression')
                body = GetByLabel('UI/Generic/FormatStandingTransactions/messageCombatAgression', locationID=transaction.locationID, ownerName=cfg.eveowners.Get(transaction.otherOwnerID).name, typeID=transaction.otherTypeID)
            elif transaction.eventTypeID == logConst.eventSecStatusKillPirateNpc:
                subject = GetByLabel('UI/Generic/FormatStandingTransactions/subjectLawEnforcmentGain')
                body = GetByLabel('UI/Generic/FormatStandingTransactions/messageLawEnforcmentGain', name=cfg.eveowners.Get(transaction.otherOwnerID).name)
            elif transaction.eventTypeID == logConst.eventSecStatusHandInTags:
                subject = GetByLabel('UI/Generic/FormatStandingTransactions/subjectHandInTags')
                body = GetByLabel('UI/Generic/FormatStandingTransactions/messageHandInTags')
            if transaction.modification is not None:
                modification = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SecurityStatusScroll/Persentage', value=transaction.modification * 100.0, decimalPlaces=4)
            else:
                modification = ''
            text = '%s<t>%s<t><right>%s</right><t>%s' % (FmtDate(transaction.eventDate, 'ls'),
             modification,
             localization.formatters.FormatNumeric(transaction.newValue, decimalPlaces=2),
             subject)
            hint = '%s<br>%s' % (localization.formatters.FormatNumeric(transaction.newValue, decimalPlaces=4), subject)
            scrolllist.append(entries.Get('StandingTransaction', {'sort_%s' % GetByLabel('UI/Common/Date'): transaction.eventDate,
             'sort_%s' % GetByLabel('UI/Common/Change'): transaction.modification,
             'line': 1,
             'text': text,
             'hint': hint,
             'details': body,
             'isNPC': True}))

        headers = [GetByLabel('UI/Common/Date'),
         GetByLabel('UI/Common/Change'),
         GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SecurityStatus'),
         GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SecurityStatusScroll/Subject')]
        noChangesHint = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SecurityStatusScroll/NoSecurityStatusChanges')
        self.scroll.Load(contentList=scrolllist, headers=headers, noContentHint=noChangesHint)
