#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\__init__.py


def ChangeSignalConnect(signalAndCallbackList, connect = True):
    for signal, callback in signalAndCallbackList:
        if connect:
            signal.connect(callback)
        else:
            signal.disconnect(callback)
