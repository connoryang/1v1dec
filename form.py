#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\modules\nice\client\_nastyspace\form.py
from carbonui.control.calendarCore import Calendar
from carbonui.util.uiAnimationTest import TestAnimationsWnd as UIAnimationTest
from eve.client.script.ui.services.careerFunnelWindow import CareerFunnelWindow
from eve.client.script.ui.services.tutorialWindow import TutorialWindow
from eve.client.script.ui.shared.neocom.addressBook.manageLabels import ManageLabels
from eve.devtools.script.uiDebugger import UIDebugger
from eve.devtools.script.uiEventListener import UIEventListener
from eve.client.script.parklife.transmissionMgr import Telecom
from eve.client.script.ui.control.fileDialog import FileDialog
from eve.client.script.ui.control.hybridWindow import HybridWindow
from eve.client.script.ui.control.listgroup import VirtualGroupWindow
from eve.client.script.ui.control.listwindow import ListWindow
from eve.client.script.ui.control.scenecontainer import SceneContainer
from eve.client.script.ui.control.scenecontainer import SceneContainerBaseNavigation
from eve.client.script.ui.control.scenecontainer import SceneContainerBrackets
from eve.client.script.ui.control.scenecontainer import SceneWindowTest
from eve.client.script.ui.crate.window import CrateWindow
from eve.client.script.ui.extras.tourneyBanUI import TourneyBanUI
from eve.client.script.ui.hacking.hackingWindow import hackingWindow as HackingWindow
from eve.client.script.ui.inflight.actions import ActionPanel
from eve.client.script.ui.inflight.activeitem import ActiveItem
from eve.client.script.ui.inflight.bountyEscrowWnd import BountyEscrowWnd
from eve.client.script.ui.inflight.capitalnavigation import CapitalNav
from eve.client.script.ui.inflight.drone import DroneView
from eve.client.script.ui.inflight.dungeoneditor import DungeonEditor
from eve.client.script.ui.inflight.dungeoneditor import DungeonObjectProperties
from eve.client.script.ui.inflight.facilityTaxWindow import FacilityTaxWindow
from eve.client.script.ui.inflight.infrastructureHub import InfrastructureHubWnd
from eve.client.script.ui.inflight.moonmining import MoonMining
from eve.client.script.ui.inflight.moonmining import SelectSiloType
from eve.client.script.ui.inflight.orbitalConfiguration import OrbitalConfigurationWindow
from eve.client.script.ui.inflight.overview import OverView
from eve.client.script.ui.inflight.scannerfiltereditor import ScannerFilterEditor
from eve.client.script.ui.inflight.shipscan import CargoScan
from eve.client.script.ui.inflight.shipscan import ShipScan
from eve.client.script.ui.inflight.surveyscan import SurveyScanView
from eve.client.script.ui.login.characterCreationLayer import CCConfirmationWindow
from eve.client.script.ui.login.intro import Intro
from eve.client.script.ui.login.loginII import Login as LoginII
from eve.client.script.ui.mapCmdWindow import MapCmdWindow
from eve.client.script.ui.services.bugReporting import BugReportingWindow
from eve.client.script.ui.services.bugReporting import ScreenshotEditingWnd
from eve.client.script.ui.services.flightPredictionSvc import FlightPredictionTestWindow
from eve.client.script.ui.shared.info.infoWindow import EntityWindow
from eve.client.script.ui.shared.info.infoWindow import PortraitWindow
from eve.client.script.ui.shared.info.infosvc import InfoWindow as infowindow
from eve.client.script.ui.services.redeemsvc import RedeemWindow
from eve.client.script.ui.services.standingsvc import StandingCompositionsWnd
from eve.client.script.ui.services.standingsvc import StandingTransactionsWnd
from eve.client.script.ui.shared.AuditLogSecureContainerLogViewer import AuditLogSecureContainerLogViewer
from eve.client.script.ui.shared.activateMultiTraining import ActivateMultiTrainingWindow
from eve.client.script.ui.shared.activatePlex import ActivatePlexWindow
from eve.client.script.ui.shared.addressBookWindow import AddressBookWindow as AddressBook
from eve.client.script.ui.shared.agentFinder import AgentFinderWnd
from eve.client.script.ui.shared.assetsWindow import AssetsWindow
from eve.client.script.ui.shared.autopilotSettings import AutopilotSettings
from eve.client.script.ui.shared.bookmarkFolderWindow import BookmarkFolderWindow
from eve.client.script.ui.shared.bookmarkLocationWindow import BookmarkLocationWindow
from eve.client.script.ui.shared.bountyWindow import BountyPicker
from eve.client.script.ui.shared.bountyWindow import BountyWindow
from eve.client.script.ui.shared.comtool.lscchannel import Channel as LSCChannel
from eve.client.script.ui.shared.comtool.lscchannel import LSCStack
from eve.client.script.ui.shared.comtool.lscengine import ChannelSettingsDialog
from eve.client.script.ui.shared.comtool.lscengine import ChatInviteWnd
from eve.client.script.ui.shared.comtool.lscengine import PCOwnerPickerDialog
from eve.client.script.ui.shared.ctrltab import CtrlTabWindow
from eve.client.script.ui.shared.eveCalendar import CalendarNewEventWnd
from eve.client.script.ui.shared.eveCalendar import CalendarSingleDayWnd
from eve.client.script.ui.shared.eveCalendar import Calendar as eveCalendar
from eve.client.script.ui.shared.eveCalendar import CalendarWnd as eveCalendarWnd
from eve.client.script.ui.shared.export import ExportBaseWindow
from eve.client.script.ui.shared.export import ExportFittingsWindow
from eve.client.script.ui.shared.export import ExportOverviewWindow
from eve.client.script.ui.shared.export import ImportBaseWindow
from eve.client.script.ui.shared.export import ImportFittingsWindow
from eve.client.script.ui.shared.export import ImportLegacyFittingsWindow
from eve.client.script.ui.shared.export import ImportOverviewWindow
from eve.client.script.ui.shared.factionalWarfare.infrastructureHub import FWInfrastructureHub
from eve.client.script.ui.shared.fittingMgmtWindow import FittingMgmt
from eve.client.script.ui.shared.fittingMgmtWindow import ViewFitting
from eve.client.script.ui.shared.fleet.fleet import FleetView
from eve.client.script.ui.shared.fleet.fleet import WatchListPanel
from eve.client.script.ui.shared.fleet.fleetbroadcast import BroadcastSettings
from eve.client.script.ui.shared.fleet.fleetbroadcast import FleetBroadcastView
from eve.client.script.ui.shared.fleet.fleetfinder import FleetFinderWindow
from eve.client.script.ui.shared.fleet.fleetregister import RegisterFleetWindow
from eve.client.script.ui.shared.fleet.fleetwindow import FleetComposition
from eve.client.script.ui.shared.fleet.fleetwindow import FleetJoinRequestWindow
from eve.client.script.ui.shared.fleet.fleetwindow import FleetWindow
from eve.client.script.ui.shared.inventory.filterSvc import FilterCreationWindow
from eve.client.script.ui.shared.inventory.invWindow import ActiveShipCargo
from eve.client.script.ui.shared.inventory.invWindow import Inventory
from eve.client.script.ui.shared.inventory.invWindow import InventoryPrimary
from eve.client.script.ui.shared.inventory.invWindow import StationCorpDeliveries
from eve.client.script.ui.shared.inventory.invWindow import StationCorpHangars
from eve.client.script.ui.shared.inventory.invWindow import StationItems
from eve.client.script.ui.shared.inventory.invWindow import StationShips
from eve.client.script.ui.shared.killReport import KillReportWnd
from eve.client.script.ui.shared.killRights import SellKillRightWnd
from eve.client.script.ui.shared.maps.browserwindow import MapBrowserWnd
from eve.client.script.ui.shared.maps.palette import MapPalette as MapsPalette
from eve.client.script.ui.shared.market.marketbase import MarketBase as Market
from eve.client.script.ui.shared.market.marketbase import MarketData
from eve.client.script.ui.shared.market.marketbase import RegionalMarket
from eve.client.script.ui.shared.market.marketbase import StationMarket
from eve.client.script.ui.shared.market.orders import MarketOrders
from eve.client.script.ui.shared.market.quote import MarketActionWindow
from eve.client.script.ui.shared.market.sellMulti import SellItems
from eve.client.script.ui.shared.medalribbonranks import MedalRibbonPickerWindow
from eve.client.script.ui.shared.messagebox import MessageBox
from eve.client.script.ui.shared.monetization.trialPopup import TrialPopup
from eve.client.script.ui.shared.neocom.Alliances.all_ui_alliances import FormAlliances as Alliances
from eve.client.script.ui.shared.neocom.Alliances.all_ui_applications import FormAlliancesApplications as AlliancesApplications
from eve.client.script.ui.shared.neocom.Alliances.all_ui_applications import ApplyToAllianceWnd
from eve.client.script.ui.shared.neocom.Alliances.all_ui_applications import MyAllianceApplicationWnd
from eve.client.script.ui.shared.neocom.Alliances.all_ui_home import FormAlliancesBulletins as AlliancesBulletins
from eve.client.script.ui.shared.neocom.Alliances.all_ui_home import FormAlliancesHome as AlliancesHome
from eve.client.script.ui.shared.neocom.Alliances.all_ui_home import CreateAllianceWnd
from eve.client.script.ui.shared.neocom.Alliances.all_ui_home import EditAllianceWnd
from eve.client.script.ui.shared.neocom.Alliances.all_ui_home import SetShortNameWnd
from eve.client.script.ui.shared.neocom.Alliances.all_ui_members import FormAlliancesMembers as AlliancesMembers
from eve.client.script.ui.shared.neocom.Alliances.all_ui_rankings import FormAlliancesRankings as AlliancesRankings
from eve.client.script.ui.shared.neocom.addressBook.contactManagementMultiEditWindow import ContactManagementMultiEditWnd
from eve.client.script.ui.shared.neocom.addressBook.contactManagementWindow import ContactManagementWnd
from eve.client.script.ui.shared.neocom.addressBook.contactsForm import ContactsForm
from eve.client.script.ui.shared.neocom.addressBook.corpAllianceContactManagementWindow import CorpAllianceContactManagementWnd
from eve.client.script.ui.shared.neocom.attributes import AttributeRespecWindow as attributeRespecWindow
from eve.client.script.ui.shared.neocom.calculator import Calculator
from eve.client.script.ui.shared.neocom.channels import Channels
from eve.client.script.ui.shared.neocom.characterSheetWindow import CharacterSheetWindow as CharacterSheet
from eve.client.script.ui.shared.neocom.compare import TypeCompare
from eve.client.script.ui.shared.neocom.contracts.contractsDetailsWnd import ContractDetailsWindow
from eve.client.script.ui.shared.neocom.contracts.contractsWnd import ContractsWindow
from eve.client.script.ui.shared.neocom.contracts.createContractWnd import CreateContractWnd
from eve.client.script.ui.shared.neocom.contracts.ignoreListWnd import IgnoreListWindow
from eve.client.script.ui.shared.neocom.contracts.contractsearch import ContractSearchWindow
from eve.client.script.ui.shared.neocom.corporation.base_corporation_ui import CorporationWindow as Corporation
from eve.client.script.ui.shared.neocom.corporation.corp_dlg_edit_member import EditMemberDialog
from eve.client.script.ui.shared.neocom.corporation.corp_dlg_editcorpdetails import CorpDetails
from eve.client.script.ui.shared.neocom.corporation.corp_dlg_editcorpdetails import CreateCorp
from eve.client.script.ui.shared.neocom.corporation.corp_dlg_editcorpdetails import EditCorpDetails
from eve.client.script.ui.shared.neocom.corporation.corp_ui_accounts import CorpAccounts
from eve.client.script.ui.shared.neocom.corporation.corp_ui_applications import ApplyToCorpWnd
from eve.client.script.ui.shared.neocom.corporation.corp_ui_applications import MyCorpApplicationWnd
from eve.client.script.ui.shared.neocom.corporation.corp_ui_applications import InviteToCorpWnd
from eve.client.script.ui.shared.neocom.corporation.corp_ui_applications import RejectCorpApplicationWnd
from eve.client.script.ui.shared.neocom.corporation.corp_ui_applications import ViewCorpApplicationWnd
from eve.client.script.ui.shared.neocom.corporation.corp_ui_home import CorpUIHome
from eve.client.script.ui.shared.neocom.corporation.corp_ui_home import EditCorpBulletin
from eve.client.script.ui.shared.neocom.corporation.corp_ui_member_auditing import CorpAuditing
from eve.client.script.ui.shared.neocom.corporation.corp_ui_member_decorations import CorpDecorations
from eve.client.script.ui.shared.neocom.corporation.corp_ui_member_find import CorpFindMembersInRole
from eve.client.script.ui.shared.neocom.corporation.corp_ui_member_find import CorpQueryMembersForm
from eve.client.script.ui.shared.neocom.corporation.corp_ui_member_newroles import CorpRolesNew
from eve.client.script.ui.shared.neocom.corporation.corp_ui_member_titles import CorpTitles
from eve.client.script.ui.shared.neocom.corporation.corp_ui_member_tracking import CorpMemberTracking
from eve.client.script.ui.shared.neocom.corporation.corp_ui_member_view_role_mgt import CorpMembersViewRoleManagement
from eve.client.script.ui.shared.neocom.corporation.corp_ui_member_view_simple import CorpMembersViewSimple
from eve.client.script.ui.shared.neocom.corporation.corp_ui_member_view_task_mgt import CorpMembersViewTaskManagement
from eve.client.script.ui.shared.neocom.corporation.corp_ui_members import CorpMembers
from eve.client.script.ui.shared.neocom.corporation.corp_ui_recruitment import CorpApplicationContainer
from eve.client.script.ui.shared.neocom.corporation.corp_ui_recruitment import CorpRecruitment
from eve.client.script.ui.shared.neocom.corporation.corp_ui_sanctionableactions import CorpSanctionableActions
from eve.client.script.ui.shared.neocom.corporation.corp_ui_standings import CorpStandings
from eve.client.script.ui.shared.neocom.corporation.corp_ui_standings import CorporationOrAlliancePickerDailog
from eve.client.script.ui.shared.neocom.corporation.corp_ui_votes import CorpVotes
from eve.client.script.ui.shared.neocom.corporation.corp_ui_votes import VoteWizardDialog
from eve.client.script.ui.shared.neocom.corporation.corp_ui_votes import WizardDialogBase
from eve.client.script.ui.shared.neocom.corporation.corp_ui_wars import CorpWars
from eve.client.script.ui.shared.neocom.corporation.warReport import WarReportWnd
from eve.client.script.ui.shared.neocom.corporation.warWindows import AllyWnd
from eve.client.script.ui.shared.neocom.corporation.warWindows import NegotiationWnd
from eve.client.script.ui.shared.neocom.corporation.warWindows import WarAssistanceOfferWnd
from eve.client.script.ui.shared.neocom.corporation.warWindows import WarSurrenderWnd
from eve.client.script.ui.shared.neocom.evemail import MailSearchWindow
from eve.client.script.ui.shared.neocom.evemail import MailForm
from eve.client.script.ui.shared.neocom.evemail import MailReadingWnd
from eve.client.script.ui.shared.neocom.evemail import MailSettings
from eve.client.script.ui.shared.neocom.evemail import MailWindow
from eve.client.script.ui.shared.neocom.evemail import MailinglistWnd
from eve.client.script.ui.shared.neocom.evemail import ManageLabelsBase
from eve.client.script.ui.shared.neocom.evemail import ManageLabelsExistingMails
from eve.client.script.ui.shared.neocom.evemail import ManageLabelsNewMails
from eve.client.script.ui.shared.neocom.evemail import NewNewMessage
from eve.client.script.ui.shared.neocom.evemailingListConfig import MaillistSetupWindow
from eve.client.script.ui.shared.neocom.help import HelpWindow
from eve.client.script.ui.shared.neocom.journal import JournalWindow as Journal
from eve.client.script.ui.shared.neocom.notepad import NotepadWindow as Notepad
from eve.client.script.ui.shared.neocom.notifications import NotificationForm
from eve.client.script.ui.shared.neocom.ownerSearch import OwnerSearchWindow
from eve.client.script.ui.shared.neocom.petition import PetitionWindow
from eve.client.script.ui.shared.neocom.skillqueueUI import SkillQueue
from eve.client.script.ui.shared.neocom.wallet import GiveSharesDialog
from eve.client.script.ui.shared.neocom.wallet import NoneNPCAccountOwnerDialog
from eve.client.script.ui.shared.neocom.wallet import TransferMoneyWnd
from eve.client.script.ui.shared.neocom.wallet import WalletWindow as Wallet
from eve.client.script.ui.shared.neocom.wallet import WalletContainer
from eve.client.script.ui.shared.vgs.offerWindow import OfferWindow
from eve.client.script.ui.shared.planet.depletionPinManager import DepletionManager
from eve.client.script.ui.shared.planet.expeditedTransferUI import ExpeditedTransferManagementWindow
from eve.client.script.ui.shared.planet.importExportUI import PlanetaryImportExportUI
from eve.client.script.ui.shared.planet.orbitalMaterialUI import OrbitalMaterialUI
from eve.client.script.ui.shared.planet.planetWindow import PlanetWindow
from eve.client.script.ui.shared.planet.surveyUI import SurveyWindow as PlanetSurvey
from eve.client.script.ui.shared.preview import PreviewWnd
from eve.client.script.ui.shared.preview import PreviewCharacterWnd
from eve.client.script.ui.shared.radioButtonMessageBox import RadioButtonMessageBox
from eve.client.script.ui.shared.shipconfig import ShipConfig
from eve.client.script.ui.shared.systemMenu.systemmenu import SystemMenu
from eve.client.script.ui.shared.systemMenu.systemmenu import VoiceFontSelectionWindow
from eve.client.script.ui.shared.uilog import LoggerWindow as Logger
from eve.client.script.ui.shared.twitch.twitchStreaming import TwitchStreaming
from eve.client.script.ui.skilltrading.skillExtractorWindow import SkillExtractorWindow
from eve.client.script.ui.station.agents.agentDialogueWindow import AgentDialogueWindow
from eve.client.script.ui.station.agents.agents import AgentBrowser
from eve.client.script.ui.station.assembleModularShip import AssembleShip
from eve.client.script.ui.station.base import StationLayer
from eve.client.script.ui.station.captainsquarters.mainScreen import MainScreenTestWindow as MainScreenTest
from eve.client.script.ui.station.fw.base_fw import MilitiaWindow
from eve.client.script.ui.station.insurance.base_insurance import InsuranceWindow
from eve.client.script.ui.station.lobby import Lobby
from eve.client.script.ui.station.lpstore import LPExhangeDialog
from eve.client.script.ui.station.lpstore import LPStoreWindow as LPStore
from eve.client.script.ui.station.lpstore import LPStoreFiltersWindow as LPStoreFilters
from eve.client.script.ui.station.medical.medical import MedicalWindow
from eve.client.script.ui.station.medical.cloneStation import CloneStationWindow
from eve.client.script.ui.station.pvptrade.pvptradewnd import PVPTrade
from eve.client.script.ui.station.repairshop.base_repairshop import RepairShopWindow
from eve.client.script.ui.station.stationmanagement.base_stationmanagement import StationManagement
from eve.client.script.ui.station.stationmanagement.base_stationmanagement import StationManagementDialog
from eve.client.script.ui.station.stationmanagement.facilityStandingsWindow import FacilityStandingsWindow
from eve.client.script.ui.util.gradientEdit import GradientEditor
from eve.client.script.ui.util.namedPopup import NamePopupWnd
from eve.devtools.script.alignmentTest import AlignmentTester
from eve.devtools.script.autoMoveBot import AutoMoveBotWnd as autoMoveBot
from eve.devtools.script.colors import ColorPicker as UIColorPicker
from eve.devtools.script.connectiontest import ConnectionLoopTest as ConnLoop
from eve.devtools.script.form_sounds import InsiderSoundPlayer
from eve.devtools.script.form_tournament import TournamentWindow as tournament
from eve.devtools.script.form_viewer import BinkVideoViewer as InsiderBinkVideoViewer
from eve.devtools.script.insider import InsiderWnd
from eve.devtools.script.spaminator import DetentionSnippetWnd
from eve.devtools.script.svc_ballparkExporter import BallparkExporter
from eve.devtools.script.svc_cspam import ChannelSpamForm as cspam
from eve.devtools.script.svc_dgmattr import AttributeInspector
from eve.devtools.script.svc_invtools import InvToolsWnd as invTools
from eve.devtools.script.svc_poser import AssembleWindow
from eve.devtools.script.svc_poser import FuelWindow
from eve.devtools.script.svc_settingsMgr import SettingsMgr
from eve.devtools.script.tournamentRefereeTools import RefWindowSpawningWindow
from eve.devtools.script.tournamentRefereeTools import TournamentRefereeTool
from eve.devtools.script.uiScaling import UIScaling
from eve.devtools.script.uiSpriteTest import UISpriteTest
from eve.devtools.script.windowManager import WindowManager
from eve.devtools.script.windowMonitor import WindowMonitor
from eve.devtools.script.localizationUtil.localization_window import LocalizationWindow as UILocalizationWindow
from reprocessing.ui.reprocessingWnd import ReprocessingWnd