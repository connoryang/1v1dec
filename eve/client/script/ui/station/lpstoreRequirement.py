#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\station\lpstoreRequirement.py
from util import FmtAmt, FmtISK
PARENT_CONTAINER_SUFFIX = 'Parent'
NOT_FULFILLED_ICON_SUFFIX = 'NotFulfilledIcon'
LABEL_SUFFIX = 'Label'

def getContainerName(requirement):
    requirementName = getattr(requirement, 'name', '')
    return requirementName + PARENT_CONTAINER_SUFFIX


def getNotFulfilledIconName(requirement):
    requirementName = getattr(requirement, 'name', '')
    return requirementName + NOT_FULFILLED_ICON_SUFFIX


def getLabelName(requirement):
    requirementName = getattr(requirement, 'name', '')
    return requirementName + LABEL_SUFFIX


class LpStoreRequirement:

    def __init__(self, name = '', amountName = '', checkAmountFunction = None, amountHintPath = None, notFulfilledHintPath = None, costLabelPath = None, priceLabelPath = None, *args, **kwargs):
        self.name = name
        self.amountName = amountName
        self.checkAmountFunction = checkAmountFunction
        self.amountHintPath = amountHintPath
        self.notFulfilledHintPath = notFulfilledHintPath
        self.costLabelPath = costLabelPath
        self.priceLabelPath = priceLabelPath

    def formatAmount(self, amount):
        return amount

    def checkAmount(self, amount):
        if self.checkAmountFunction:
            return self.checkAmountFunction() >= amount
        return True


class LpRequirement(LpStoreRequirement):
    LP_REQUIREMENT_NAME = 'lpCost'
    LP_AMOUNT_NAME = 'lpAmount'
    LP_AMOUNT_HINT_PATH = 'UI/LPStore/AmountLP'
    LP_NOT_FULFILLED_HINT_PATH = 'UI/LPStore/HintInsufficientLPs'
    LP_COST_LABEL_PATH = 'UI/LPStore/LPCost'
    LP_PRICE_LABEL_PATH = 'UI/LPStore/PriceInLP'

    def __init__(self, *args, **kwargs):
        LpStoreRequirement.__init__(self, name=self.LP_REQUIREMENT_NAME, amountName=self.LP_AMOUNT_NAME, amountHintPath=self.LP_AMOUNT_HINT_PATH, notFulfilledHintPath=self.LP_NOT_FULFILLED_HINT_PATH, costLabelPath=self.LP_COST_LABEL_PATH, priceLabelPath=self.LP_PRICE_LABEL_PATH, *args, **kwargs)
        self.formatAmount = FmtAmt


class ISKRequirement(LpStoreRequirement):
    ISK_REQUIREMENT_NAME = 'iskCost'
    ISK_AMOUNT_NAME = 'iskCost'
    ISK_AMOUNT_HINT_PATH = None
    ISK_NOT_FULFILLED_HINT_PATH = 'UI/LPStore/HintInsufficientISK'
    ISK_COST_LABEL_PATH = 'UI/LPStore/ISKCost'
    ISK_PRICE_LABEL_PATH = None

    def __init__(self, *args, **kwargs):
        LpStoreRequirement.__init__(self, name=self.ISK_REQUIREMENT_NAME, amountName=self.ISK_AMOUNT_NAME, amountHintPath=self.ISK_AMOUNT_HINT_PATH, notFulfilledHintPath=self.ISK_NOT_FULFILLED_HINT_PATH, costLabelPath=self.ISK_COST_LABEL_PATH, priceLabelPath=self.ISK_PRICE_LABEL_PATH, *args, **kwargs)
        self.formatAmount = FmtISK


class AnalysisKreditsRequirement(LpStoreRequirement):
    AK_REQUIREMENT_NAME = 'akCost'
    AK_AMOUNT_NAME = 'akAmount'
    AK_AMOUNT_HINT_PATH = 'UI/LPStore/AmountAK'
    AK_NOT_FULFILLED_HINT_PATH = 'UI/LPStore/HintInsufficientAKs'
    AK_COST_LABEL_PATH = 'UI/LPStore/AKCost'
    AK_PRICE_LABEL_PATH = 'UI/LPStore/PriceInAK'

    def __init__(self, *args, **kwargs):
        LpStoreRequirement.__init__(self, name=self.AK_REQUIREMENT_NAME, amountName=self.AK_AMOUNT_NAME, amountHintPath=self.AK_AMOUNT_HINT_PATH, notFulfilledHintPath=self.AK_NOT_FULFILLED_HINT_PATH, costLabelPath=self.AK_COST_LABEL_PATH, priceLabelPath=self.AK_PRICE_LABEL_PATH, *args, **kwargs)
        self.formatAmount = FmtAmt
