#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\net\machoNetExceptions.py
import exceptions

class MachoException(StandardError):
    __guid__ = 'exceptions.MachoException'

    def __init__(self, payload = None):
        self.payload = payload

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return '<%s: payload=%s>' % (self.__class__.__name__, self.payload)


class UberMachoException(MachoException):
    __guid__ = 'exceptions.UberMachoException'

    def __init__(self, payload = None):
        MachoException.__init__(self, payload)

    def __repr__(self):
        payload = []
        for each in self.payload:
            try:
                if each[0]:
                    payload.append('%d: %s' % (each[1], strx(each[2]) + strx(getattr(each[2], '__dict__', ''))))
            except:
                payload.append(repr(each))

        return '<%s: payload=%s>' % (self.__class__.__name__, strx(payload))


class MachoWrappedException(MachoException):
    __guid__ = 'exceptions.MachoWrappedException'

    def __init__(self, payload = None):
        MachoException.__init__(self, payload)


class UnMachoDestination(MachoException):
    __guid__ = 'exceptions.UnMachoDestination'

    def __init__(self, payload = None):
        MachoException.__init__(self, payload)


class UnMachoChannel(MachoException):
    __guid__ = 'exceptions.UnMachoChannel'

    def __init__(self, payload = None):
        MachoException.__init__(self, payload)


class WrongMachoNode(MachoException):
    __guid__ = 'exceptions.WrongMachoNode'
    __passbyvalue__ = 1

    def __init__(self, payload = None):
        MachoException.__init__(self, payload)


class ProxyRedirect(MachoException):
    __guid__ = 'exceptions.ProxyRedirect'
    __passbyvalue__ = 1

    def __init__(self, payload = None, **keywords):
        MachoException.__init__(self, payload)
        self.extra = keywords


class SessionUnavailable(MachoException):
    __guid__ = 'exceptions.SessionUnavailable'
    __passbyvalue__ = 1

    def __init__(self, payload = None):
        MachoException.__init__(self, payload)


class UserRejectedByVIP(MachoException):
    __guid__ = 'exceptions.UserRejectedByVIP'


import __builtin__
__builtin__.MachoException = MachoException
__builtin__.MachoWrappedException = MachoWrappedException
__builtin__.UnMachoDestination = UnMachoDestination
__builtin__.UnMachoChannel = UnMachoChannel
__builtin__.WrongMachoNode = WrongMachoNode
__builtin__.ProxyRedirect = ProxyRedirect
__builtin__.UberMachoException = UberMachoException
__builtin__.SessionUnavailable = SessionUnavailable
exceptions.MachoException = MachoException
exceptions.MachoWrappedException = MachoWrappedException
exceptions.UnMachoDestination = UnMachoDestination
exceptions.UnMachoChannel = UnMachoChannel
exceptions.WrongMachoNode = WrongMachoNode
exceptions.ProxyRedirect = ProxyRedirect
exceptions.UberMachoException = UberMachoException
exceptions.SessionUnavailable = SessionUnavailable
exports = {'macho.MachoException': MachoException,
 'macho.MachoWrappedException': MachoWrappedException,
 'macho.UnMachoDestination': UnMachoDestination,
 'macho.UnMachoChannel': UnMachoChannel,
 'macho.WrongMachoNode': WrongMachoNode}
