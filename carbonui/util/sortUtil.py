#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\util\sortUtil.py


def Sort(lst):
    lst.sort(lambda x, y: cmp(str(x).upper(), str(y).upper()))
    return lst


def SortListOfTuples(lst, reverse = 0):
    lst = sorted(lst, reverse=reverse, key=lambda data: data[0])
    return [ item[1] for item in lst ]


def SortByAttribute(lst, attrname = 'name', idx = None, reverse = 0):
    newlst = []
    for item in lst:
        if idx is None:
            newlst.append((getattr(item, attrname, None), item))
        else:
            newlst.append((getattr(item[idx], attrname, None), item))

    ret = SortListOfTuples(newlst, reverse)
    return ret
