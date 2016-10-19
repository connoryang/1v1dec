#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\modules\nice\client\_nastyspace\contractutils.py
from eve.common.script.util.contractscommon import CONTRACTS_PER_PAGE
from eve.common.script.util.contractscommon import CONTYPE_AUCTIONANDITEMECHANGE
from eve.common.script.util.contractscommon import CREATECONTRACT_CONFIRM_CHARGESTOHANGAR
from eve.common.script.util.contractscommon import CalcContractFees
from eve.common.script.util.contractscommon import CanRequestType
from eve.common.script.util.contractscommon import DAY
from eve.common.script.util.contractscommon import EXPIRE_TIMES
from eve.common.script.util.contractscommon import GetContractStatusText
from eve.common.script.util.contractscommon import GetContractTitle
from eve.common.script.util.contractscommon import GetContractTypeText
from eve.common.script.util.contractscommon import GetCorpRoleAtLocation
from eve.common.script.util.contractscommon import GetCurrentBid
from eve.common.script.util.contractscommon import HOUR
from eve.common.script.util.contractscommon import MAX_AMOUNT
from eve.common.script.util.contractscommon import MAX_CONTRACTS_PER_SEARCH
from eve.common.script.util.contractscommon import MAX_DESC_LENGTH
from eve.common.script.util.contractscommon import MAX_NOTES_LENGTH
from eve.common.script.util.contractscommon import MAX_NUM_CONTRACTS
from eve.common.script.util.contractscommon import MAX_NUM_ITEMS
from eve.common.script.util.contractscommon import MAX_NUM_ITEMS_TOTAL
from eve.common.script.util.contractscommon import MAX_TITLE_LENGTH
from eve.common.script.util.contractscommon import MINUTE
from eve.common.script.util.contractscommon import NUMJUMPS_UNREACHABLE
from eve.common.script.util.contractscommon import NUM_CONTRACTS_BY_SKILL
from eve.common.script.util.contractscommon import NUM_CONTRACTS_BY_SKILL_CORP
from eve.common.script.util.contractscommon import SEARCHHINT_BPC
from eve.common.script.util.contractscommon import SEARCHHINT_BPO
from eve.common.script.util.contractscommon import SECOND
from eve.common.script.util.contractscommon import SORT_ASSIGNEEID
from eve.common.script.util.contractscommon import SORT_COLLATERAL
from eve.common.script.util.contractscommon import SORT_CONSTELLATION_ID
from eve.common.script.util.contractscommon import SORT_CONTRACT_TYPE
from eve.common.script.util.contractscommon import SORT_EXPIRED
from eve.common.script.util.contractscommon import SORT_ID
from eve.common.script.util.contractscommon import SORT_PRICE
from eve.common.script.util.contractscommon import SORT_REGION_ID
from eve.common.script.util.contractscommon import SORT_REWARD
from eve.common.script.util.contractscommon import SORT_SOLARSYSTEM_ID
from eve.common.script.util.contractscommon import SORT_STATION_ID
from eve.common.script.util.contractscommon import SORT_VOLUME
from eve.common.script.util.contractscommon import WEEK
from eve.common.script.util.contractscommon import const_conBidMinimum
from eve.common.script.util.contractscommon import const_conBrokersFee
from eve.common.script.util.contractscommon import const_conBrokersFeeMaximum
from eve.common.script.util.contractscommon import const_conBrokersFeeMinimum
from eve.common.script.util.contractscommon import const_conCourierMaxVolume
from eve.common.script.util.contractscommon import const_conCourierWarningVolume
from eve.common.script.util.contractscommon import const_conDeposit
from eve.common.script.util.contractscommon import const_conDepositMaximum
from eve.common.script.util.contractscommon import const_conDepositMinimum
from eve.common.script.util.contractscommon import const_conSalesTax
from eve.common.script.util.contractscommon import const_conSalesTaxMaximum
from eve.common.script.util.contractscommon import const_conSalesTaxMinimum
from eve.client.script.util.contractutils import COL_GET
from eve.client.script.util.contractutils import COL_PAY
from eve.client.script.util.contractutils import CaseInsensitiveSubMatch
from eve.client.script.util.contractutils import CategoryName
from eve.client.script.util.contractutils import ConFmtDate
from eve.client.script.util.contractutils import CutAt
from eve.client.script.util.contractutils import DoParseItemType
from eve.client.script.util.contractutils import FmtISKWithDescription
from eve.client.script.util.contractutils import GetColoredContractStatusText
from eve.client.script.util.contractutils import GetContractIcon
from eve.client.script.util.contractutils import GetContractTimeLeftText
from eve.client.script.util.contractutils import GetMarketTypes
from eve.client.script.util.contractutils import GroupName
from eve.client.script.util.contractutils import IsIdeographic
from eve.client.script.util.contractutils import IsSearchStringLongEnough
from eve.client.script.util.contractutils import MatchInvTypeName
from eve.client.script.util.contractutils import SelectItemTypeDlg
from eve.client.script.util.contractutils import TypeName
