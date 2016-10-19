#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\seasons\common\challenge.py


class ChallengeData(object):
    agent_id = None
    challenge_id = None
    challenge_type_id = None
    character_id = None
    event_type = None
    expiration_date = None
    finish_date = None
    max_progress = None
    message_text = None
    name = None
    objective_text = None
    points_awarded = None
    progress = None
    progress_text = None
    received_date = None
    season_id = None
    start_date = None

    def __copy__(self):
        newone = ChallengeData()
        newone.__dict__.update(self.__dict__)
        return newone


class Challenge(ChallengeData):

    def __init__(self, challenge_fsd_data, challenge_db_row):
        self.agent_id = challenge_fsd_data['agent']
        self.challenge_id = challenge_db_row.challengeID
        self.challenge_type_id = challenge_db_row.challengeTypeID
        self.character_id = challenge_db_row.characterID
        self.event_type = challenge_fsd_data['event_type']
        self.expiration_date = challenge_db_row.expirationDate
        self.finish_date = challenge_db_row.finishDate
        self.is_expired = challenge_db_row.isExpired
        self.max_progress = challenge_fsd_data['max_progress']
        self.message_text = challenge_fsd_data['message_text']
        self.name = challenge_fsd_data['name']
        self.objective_text = challenge_fsd_data['objective_text']
        self.points_awarded = challenge_fsd_data['points_awarded']
        self.progress = challenge_db_row.progress
        self.progress_text = challenge_fsd_data['progress_text']
        self.always_available = challenge_fsd_data['always_available']
        self.received_date = challenge_db_row.receivedDate
        self.season_id = challenge_db_row.seasonID
        self.start_date = challenge_db_row.startDate
