#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\seasons\client\challengetaskentry.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from eve.client.script.ui.control.eveLabel import EveLabelLargeBold, Label, EveLabelSmall, EveLabelMedium
from eve.client.script.ui.eveFontConst import EVE_LARGE_FONTSIZE
from seasons.client.challengeexpirationtimer import ChallengeExpirationTimer, CHALLENGE_EXPIRATION_CLOCK_SIZE
from seasons.client.challengetaskprogressbar import ChallengeTaskProgressBar
from seasons.client.const import DEFAULT_ANIMATE_PROGRESS
from seasons.client.seasonpoints import SeasonPoints
from seasons.client.uiutils import get_agent_icon, SEASON_THEME_TEXT_COLOR_REGULAR, SEASON_THEME_TEXT_COLOR_HIGHLIGHTED
import uix
CHALLENGE_MINIMUM_HEIGHT = 120
CHALLENGE_HEIGHT_PADDING = 20
TOP_CONTAINER_MINIMUM_HEIGHT = 64
TOP_CONTAINER_PAD_TOP = 6
TOP_CONTAINER_PAD_LEFT = 10
TOP_CONTAINER_PAD_RIGHT = 10
DESCRIPTION_CONTAINER_PAD_TOP = 5
DESCRIPTION_FONTSIZE = 10
CHALLENGE_PROGRESS_HEIGHT = 20
CHALLENGE_PROGRESS_PAD_TOP = 4
CHALLENGE_PROGRESS_PAD_BOTTOM = 6
CHALLENGE_POINTS_HEIGHT = CHALLENGE_PROGRESS_HEIGHT - CHALLENGE_PROGRESS_PAD_TOP - CHALLENGE_PROGRESS_PAD_BOTTOM
CHALLENGE_POINTS_LEFT = 15
AGENT_IMAGE_SIZE = TOP_CONTAINER_MINIMUM_HEIGHT
TITLE_CONTAINER_HEIGHT = 15
TITLE_LABEL_WIDTH_OFFSET = AGENT_IMAGE_SIZE + CHALLENGE_EXPIRATION_CLOCK_SIZE + 20
CHALLENGE_EXPIRATION_CLOCK_PAD_RIGHT = 20
BACKGROUND_FILL_COLOR = (0.5, 0.5, 0.5, 0.1)
AGENT_FRAME_COLOR = (1.0, 1.0, 1.0)
AGENT_FRAME_OPACITY = 0.3

def calculate_challenges_height(challenges, challenge_text_width, are_challenges_in_two_columns):
    if are_challenges_in_two_columns:
        return calculate_challenges_height_in_two_columns(challenges, challenge_text_width)
    return calculate_challenges_height_in_one_column(challenges, challenge_text_width)


def calculate_challenges_height_in_one_column(challenges, challenge_text_width):
    challenges_height = 0
    challenge_entries_height = dict()
    for challenge in challenges.itervalues():
        total_challenge_height, title_text_height, description_text_height = calculate_challenge_height(challenge, challenge_text_width)
        challenge_entries_height[challenge.challenge_id] = [total_challenge_height, title_text_height, description_text_height]
        challenges_height += total_challenge_height

    return (challenges_height, challenge_entries_height)


def calculate_challenges_height_in_two_columns(challenges, challenge_text_width):
    challenges_height = 0
    challenge_entries_height = dict()
    challenges_in_column_one = []
    challenges_in_column_two = []
    challenge_count = 1
    for challenge in challenges.itervalues():
        if challenge_count % 2:
            challenges_in_column_one.append(challenge)
        else:
            challenges_in_column_two.append(challenge)
        challenge_count += 1

    number_of_rows = challenge_count / 2
    for row in xrange(0, number_of_rows):
        challenge_one = challenges_in_column_one[row]
        challenge_one_height, challenge_one_title_text_height, challenge_one_description_text_height = calculate_challenge_height(challenge_one, challenge_text_width)
        challenge_height = challenge_one_height
        is_there_column_two = row < len(challenges_in_column_two)
        if is_there_column_two:
            challenge_two = challenges_in_column_two[row]
            challenge_two_height, challenge_two_title_text_height, challenge_two_description_text_height = calculate_challenge_height(challenge_two, challenge_text_width)
            challenge_height = max(challenge_one_height, challenge_two_height)
            challenge_entries_height[challenge_two.challenge_id] = [challenge_height, challenge_two_title_text_height, challenge_two_description_text_height]
        challenge_entries_height[challenge_one.challenge_id] = [challenge_height, challenge_one_title_text_height, challenge_one_description_text_height]
        challenges_height += challenge_height

    return (challenges_height, challenge_entries_height)


def calculate_challenge_height(challenge, text_width):
    text_width = text_width - 2 * TOP_CONTAINER_PAD_LEFT - TOP_CONTAINER_PAD_RIGHT
    title_text_height = uix.GetTextHeight(strng=challenge.name, width=text_width, font=EVE_LARGE_FONTSIZE)
    title_text_height = max(TITLE_CONTAINER_HEIGHT, title_text_height + TOP_CONTAINER_PAD_TOP)
    description_text_height = uix.GetTextHeight(strng=challenge.message_text, width=text_width, font=DESCRIPTION_FONTSIZE) + DESCRIPTION_CONTAINER_PAD_TOP
    description_text_height += DESCRIPTION_CONTAINER_PAD_TOP
    top_height = max(TOP_CONTAINER_MINIMUM_HEIGHT, title_text_height + description_text_height + DESCRIPTION_CONTAINER_PAD_TOP)
    progress_height = CHALLENGE_PROGRESS_HEIGHT + CHALLENGE_PROGRESS_PAD_TOP + CHALLENGE_PROGRESS_PAD_BOTTOM
    total_challenge_height = max(CHALLENGE_MINIMUM_HEIGHT, top_height + progress_height) + CHALLENGE_HEIGHT_PADDING
    return (total_challenge_height, title_text_height, description_text_height)


class ChallengeTaskEntry(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.challenge = attributes.challenge
        self.challenge_title_height = attributes.challenge_title_height
        self.challenge_description_height = attributes.challenge_description_height
        self.challenge_height = self._get_challenge_height()
        self.progress_frame_width = attributes.progress_frame_width
        self.progress_frame_width_offset = attributes.progress_frame_width_reduction
        self.animate_progress = attributes.Get('animate_progress', DEFAULT_ANIMATE_PROGRESS)
        Fill(bgParent=self, color=BACKGROUND_FILL_COLOR)
        self._construct_header()
        self._construct_rewards()
        self._construct_progress()

    def _get_challenge_height(self):
        return max(TOP_CONTAINER_MINIMUM_HEIGHT, self.challenge_title_height + self.challenge_description_height)

    def _construct_header(self):
        self.top_container = Container(name='top_container', parent=self, align=uiconst.TOTOP, height=self.challenge_height, padTop=TOP_CONTAINER_PAD_TOP, padLeft=TOP_CONTAINER_PAD_LEFT, padRight=TOP_CONTAINER_PAD_RIGHT)
        self._construct_agent()
        self._construct_description()

    def _construct_agent(self):
        agent_container = Container(name='agent_container', parent=self.top_container, align=uiconst.TOLEFT, width=AGENT_IMAGE_SIZE, height=AGENT_IMAGE_SIZE)
        frame_container = Container(name='frame_container', parent=agent_container, align=uiconst.TOPLEFT, width=AGENT_IMAGE_SIZE, height=AGENT_IMAGE_SIZE)
        Frame(name='agent_icon_frame', parent=frame_container, frameConst=uiconst.FRAME_BORDER1_CORNER0, opacity=AGENT_FRAME_OPACITY, color=AGENT_FRAME_COLOR)
        get_agent_icon(name='agent_icon', parent=agent_container, align=uiconst.CENTERTOP, size=AGENT_IMAGE_SIZE, agent_id=self.challenge.agent_id)

    def _construct_description(self):
        self.title_container = Container(name='title_container', parent=self.top_container, align=uiconst.TOTOP, height=max(TITLE_CONTAINER_HEIGHT, self.challenge_title_height), padLeft=TOP_CONTAINER_PAD_LEFT)
        title_label_container_width = self.width - AGENT_IMAGE_SIZE - CHALLENGE_EXPIRATION_CLOCK_PAD_RIGHT - CHALLENGE_EXPIRATION_CLOCK_SIZE - TOP_CONTAINER_PAD_LEFT - TOP_CONTAINER_PAD_RIGHT
        self.title_label_container = Container(name='title_label_container', parent=self.title_container, align=uiconst.TOLEFT, width=title_label_container_width, clipChildren=True)
        title_label = EveLabelLargeBold(name='title_label', parent=self.title_label_container, align=uiconst.CENTERLEFT, text=self.challenge.name)
        title_label.color = SEASON_THEME_TEXT_COLOR_HIGHLIGHTED
        expiration_timer_container = Container(name='expiration_timer_container', parent=self.title_container, align=uiconst.TORIGHT, width=CHALLENGE_EXPIRATION_CLOCK_SIZE)
        ChallengeExpirationTimer(name='expiration_timer', parent=expiration_timer_container, align=uiconst.CENTER, height=CHALLENGE_EXPIRATION_CLOCK_SIZE, width=CHALLENGE_EXPIRATION_CLOCK_SIZE, expiration_date=self.challenge.expiration_date)
        description_container = Container(name='description_container', parent=self.top_container, align=uiconst.TOTOP, height=self.challenge_description_height, padLeft=TOP_CONTAINER_PAD_LEFT, padTop=DESCRIPTION_CONTAINER_PAD_TOP)
        description_label = Label(name='description_label', parent=description_container, align=uiconst.TOTOP, text=self.challenge.message_text, fontsize=DESCRIPTION_FONTSIZE)
        description_label.color = SEASON_THEME_TEXT_COLOR_REGULAR

    def _construct_rewards(self):
        reward_wrapper_container = ContainerAutoSize(name='reward_wrapper_container', parent=self, align=uiconst.TOBOTTOM_NOPUSH, height=CHALLENGE_PROGRESS_HEIGHT, padTop=CHALLENGE_PROGRESS_PAD_TOP, padBottom=CHALLENGE_PROGRESS_PAD_BOTTOM, padLeft=TOP_CONTAINER_PAD_LEFT, padRight=TOP_CONTAINER_PAD_RIGHT)
        SeasonPoints(name='reward_container', parent=reward_wrapper_container, points=self.challenge.points_awarded, season_points_size=CHALLENGE_PROGRESS_HEIGHT, reward_label_class=EveLabelMedium, align=uiconst.TORIGHT, height=CHALLENGE_POINTS_HEIGHT, left=CHALLENGE_POINTS_LEFT)

    def _construct_progress(self):
        self.progress_container = ChallengeTaskProgressBar(name='progress_container', parent=self, align=uiconst.TOBOTTOM, challenge=self.challenge, progress_frame_width=self.progress_frame_width, progress_frame_width_offset=self.progress_frame_width_offset, animate_progress=self.animate_progress, height=CHALLENGE_PROGRESS_HEIGHT, padTop=CHALLENGE_PROGRESS_PAD_TOP, padBottom=CHALLENGE_PROGRESS_PAD_BOTTOM, padLeft=TOP_CONTAINER_PAD_LEFT, padRight=TOP_CONTAINER_PAD_RIGHT, label_type_function=EveLabelSmall, adapt_text_color_to_progress=True)

    def update_challenge_progress(self, new_progress):
        self.progress_container.update_challenge(new_progress)

    def complete_challenge(self):
        self.progress_container.update_challenge(self.challenge.max_progress)
