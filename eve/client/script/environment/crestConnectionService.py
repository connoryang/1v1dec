#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\crestConnectionService.py
import service
import blue
import crestclient

class CrestConnectionService(service.Service):
    __guid__ = 'svc.crestConnectionService'
    __servicename__ = 'crestConnectionSvc'
    __displayName__ = 'Crest Connection Service'
    __configvalues__ = {'verify': 'cacert.pem'}

    def Run(self, memStream = None):
        self.LogInfo('Starting Crest Connection Service')
        self.userSession = None
        self.token = None

    def GetUserSession(self):
        if self.userSession is None:
            server = sm.RemoteSvc('crestapiService').GetExternalAddress()
            if not server:
                server = 'http://localhost:26004/'
            if self.token:
                self.LogInfo('crestUserSession init with token')
                if blue.pyos.packaged:
                    verify = blue.paths.ResolvePath(u'app:/') + self.verify
                else:
                    verify = False
                self.userSession = crestclient.CrestUserSso(self.token, server, verify, session.languageID)
            else:
                self.LogError('token missing when trying to create a crestUser Session')
                raise RuntimeError('tokenMissing')
        return self.userSession

    def SetSessionToken(self, token):
        self.LogInfo('Setting CrestConnection Token as %s' % token)
        self.token = token
