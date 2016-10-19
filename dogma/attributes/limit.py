#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\attributes\limit.py
import collections

def LimitAttributeOnItem(item, timestamp, attribute, value, length = 20):
    if item is None:
        return value
    else:
        limit = item.GetValue(attribute)
        if limit:
            return UpdateRollingLimit(GetHistory(item, attribute), timestamp, limit, value, length)
        return value


def GetAttributeLimitOnItem(item, timestamp, attribute, length = 20):
    if item:
        return GetRollingLimit(GetHistory(item, attribute), timestamp, length)


def GetHistory(item, attribute):
    try:
        return item.rollingHistory[attribute]
    except AttributeError:
        item.rollingHistory = collections.defaultdict(collections.OrderedDict)
        return item.rollingHistory[attribute]


def UpdateRollingLimit(history, timestamp, limit, value, length = 20):
    if limit and value:
        total = GetRollingLimit(history, timestamp, length)
        limit = limit * length
        value = min(value, max(limit - total, 0))
        if value == 0:
            return 0
        history[int(timestamp)] = value + history.get(int(timestamp), 0)
    return value


def GetRollingLimit(history, timestamp, length = 20):
    oldest = int(timestamp) - length
    for key in history.keys():
        if key < oldest:
            del history[key]
        else:
            break

    return sum(history.itervalues())
