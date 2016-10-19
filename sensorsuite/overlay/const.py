#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\sensorsuite\overlay\const.py
from carbon.common.lib.const import SEC
SWEEP_CYCLE_TIME_SEC = 8.0
SWEEP_CYCLE_TIME = long(SWEEP_CYCLE_TIME_SEC * SEC)
SWEEP_LEAD_TIME = long(0 * SEC)
SWEEP_TAIL_TIME = long(0.5 * SEC)
SWEEP_START_GRACE_TIME_SEC = 5.0
SWEEP_START_GRACE_TIME = long(SWEEP_START_GRACE_TIME_SEC * SEC)
SUPPRESS_GFX_WARPING = 1
SUPPRESS_GFX_NO_UI = 2
MESSAGE_ON_SENSOR_OVERLAY_ENABLED = 1
MESSAGE_ON_SENSOR_OVERLAY_DISABLED = 2
MESSAGE_ON_SENSOR_OVERLAY_SWEEP_STARTED = 3
MESSAGE_ON_SENSOR_OVERLAY_SWEEP_ENDED = 4
MESSAGE_ON_SENSOR_OVERLAY_SITE_CHANGED = 5
MESSAGE_ON_SENSOR_OVERLAY_SITE_MOVED = 6