#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\testfixtures\resolve.py
from testfixtures import not_there

def resolve(dotted_name):
    names = dotted_name.split('.')
    used = names.pop(0)
    found = __import__(used)
    container = found
    method = None
    n = None
    for n in names:
        container = found
        used += '.' + n
        try:
            found = found.__dict__[n]
            method = 'a'
        except (AttributeError, KeyError):
            try:
                found = getattr(found, n)
                method = 'a'
            except AttributeError:
                try:
                    __import__(used)
                except ImportError:
                    method = 'i'
                    try:
                        found = found[n]
                    except KeyError:
                        found = not_there
                    except TypeError:
                        try:
                            n = int(n)
                        except ValueError:
                            method = 'a'
                            found = not_there
                        else:
                            found = found[n]

                else:
                    found = getattr(found, n)
                    method = 'a'

    return (container,
     method,
     n,
     found)
