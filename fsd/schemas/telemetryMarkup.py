#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fsd\schemas\telemetryMarkup.py
from contextlib import contextmanager
try:
    import blue
    blueAvailable = True
except ImportError:
    blueAvailable = False

if blueAvailable:

    @contextmanager
    def TelemetryContext(name):
        blue.statistics.EnterZone(name)
        try:
            yield
        finally:
            blue.statistics.LeaveZone()


else:

    @contextmanager
    def TelemetryContext(name):
        yield
