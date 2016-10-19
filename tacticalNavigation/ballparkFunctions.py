#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\tacticalNavigation\ballparkFunctions.py


def GetBallpark():
    michelle = sm.GetService('michelle')
    return michelle.GetBallpark()


def GetBall(ballID):
    return sm.GetService('michelle').GetBall(ballID)


def ConvertPositionToGlobalSpace(position):
    bp = GetBallpark()
    if bp is None:
        return
    egopos = bp.GetCurrentEgoPos()
    destination = (position[0] + egopos[0], position[1] + egopos[1], position[2] + egopos[2])
    return destination


def AddClientBallLocal(localPosition):
    position = ConvertPositionToGlobalSpace(localPosition)
    if position is None:
        return
    return AddClientBall(position)


def AddClientBall(position):
    bp = GetBallpark()
    if bp is None:
        return
    return bp.AddClientSideBall(position)


def RemoveClientBall(ball):
    bp = GetBallpark()
    if bp is not None and ball.ballpark is not None:
        bp.RemoveBall(ball.id)
