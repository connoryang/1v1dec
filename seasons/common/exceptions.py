#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\seasons\common\exceptions.py


class ChallengeForCharacterNotFoundError(Exception):
    pass


class NotEnoughChallengeTypesAvailableError(Exception):
    pass


class SeasonHasAlreadyEndedError(Exception):
    pass


class ChallengeTypeNotFoundError(Exception):
    pass


class ChallengeAlreadyExpiredError(Exception):
    pass


class ChallengeAlreadyCompletedError(Exception):
    pass
