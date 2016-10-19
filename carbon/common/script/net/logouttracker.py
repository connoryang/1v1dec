#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\net\logouttracker.py
import logging
logger = logging.getLogger(__name__)

def TrackLogOut(reason, serverIp):
    import localization
    import ccpmetrics
    logger.error('LogOut: {0}'.format(reason), extra={'tags': {'reason': reason,
              'serverIp': serverIp}})
    try:
        metrics = ccpmetrics.Client('public-metrics.tech.ccp.is')
        if reason == localization.GetByLabel('/Carbon/MachoNet/SocketWasClosed'):
            logger.info('sending disconnect event')
            metrics.increment('eve_client_disconnect', tags={'serverIp': serverIp})
    except Exception:
        logger.exception('Failed to register disconnect')
