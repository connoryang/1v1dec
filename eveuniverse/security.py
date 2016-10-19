#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\eveuniverse\security.py
securityClassZeroSec = 0
securityClassLowSec = 1
securityClassHighSec = 2

def SecurityClassFromLevel(level):
    if level <= 0.0:
        return securityClassZeroSec
    elif level < 0.45:
        return securityClassLowSec
    else:
        return securityClassHighSec
