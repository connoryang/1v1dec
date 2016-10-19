#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\attributes\datetime.py
from carbon.common.lib.const import DAY, SEC
from gametime import EPOCH_BLUE_TIME
SECONDS_PER_DAY = float(DAY / SEC)

def float_as_time(value):
    time = value * DAY + EPOCH_BLUE_TIME
    return long(round(time / SEC)) * SEC


def time_as_float(time):
    return round((time - EPOCH_BLUE_TIME) / SEC) / float(DAY / SEC)
