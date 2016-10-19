#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\actionLog\client\formatters.py
import localization
STRONG_COLOR = '<color=0xff00ffff>'
FAINT_COLOR = '<color=0x77ffffff>'
NORMAL_COLOR = '<color=0xffffffff>'
BOUNTY_PAYOUT_COLOR = '<color=0xff00aa00>'
MINING_AMOUNT_COLOR = '<color=0xffaaaa00>'

def FormatBountyMessage(normalFontSize, bounty):
    return localization.GetByLabel('UI/Inflight/ActivityLog/BountyAddedToPayoutMessage1', normalFont=_GetFontSizeString(normalFontSize), bountyPayoutColor=BOUNTY_PAYOUT_COLOR, bounty=bounty, faintColor=FAINT_COLOR)


def FormatMiningMessage(normalFontSize, oreTypeID, volume, amount):
    return localization.GetByLabel('UI/Inflight/ActivityLog/MinedMessage1', faintColor=FAINT_COLOR, normalFont=_GetFontSizeString(normalFontSize), smallFont=_GetFontSizeString(normalFontSize - 2), amountMinedColor=MINING_AMOUNT_COLOR, amount=amount, normalColor=NORMAL_COLOR, oreTypeID=oreTypeID)


def _GetFontSizeString(fontSize):
    normalFont = '<font size=%s>' % str(fontSize)
    return normalFont
