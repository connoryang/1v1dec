#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\projectdiscovery\common\exceptions.py


class NotEnoughAnalysisPointsToTakeFromPlayer(ValueError):
    pass


class ClassificationTaskNotTheActiveTaskError(Exception):
    pass


class NoActiveClassificationTaskError(Exception):
    pass


class UnexpectedMmosResultError(Exception):
    pass


class NoConnectionToAPIError(Exception):
    pass


class MissingKeyError(Exception):
    pass
