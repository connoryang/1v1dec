#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\trinutils\trinfileutils.py
import os
import trinity

def SaveTrinityObject(path, trinObj, checkOutFunc = None):
    if os.path.isfile(path) and checkOutFunc is not None:
        retVal, _ = checkOutFunc(path)
        if not retVal:
            return False
    return trinity.Save(trinObj, path)
