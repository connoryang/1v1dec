#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\gpuinfo\__init__.py
import trinity

def getGpuDriverInfo(adapterInfo):
    results = {'gpu': {'driver': {}}}
    try:
        driverInfo = adapterInfo.GetDriverInfo()
        results['gpu'] = {}
        results['gpu']['driver'] = {}
        results['gpu']['driver']['Version'] = unicode(driverInfo.driverVersionString)
        results['gpu']['driver']['Date'] = unicode(driverInfo.driverDate)
        results['gpu']['driver']['Vendor'] = unicode(driverInfo.driverVendor)
        results['gpu']['driver']['IsOptimus'] = u'Yes' if driverInfo.isOptimus else u'No'
        results['gpu']['driver']['IsAmdSwitchable'] = u'Yes' if driverInfo.isAmdDynamicSwitchable else u'No'
    except trinity.ALError:
        pass

    return results


def getGpuInfo():
    adapters = trinity.adapters
    adapterInfo = adapters.GetAdapterInfo(adapters.DEFAULT_ADAPTER)
    results = getGpuDriverInfo(adapterInfo)
    results['gpu']['Description'] = unicode(adapterInfo.description)
    results['gpu']['Driver'] = unicode(adapterInfo.driver)
    results['gpu']['VendorId'] = unicode(adapterInfo.vendorID)
    results['gpu']['DeviceId'] = unicode(adapterInfo.deviceID)
    results['gpu']['TrinityPlatform'] = unicode(trinity.platform)
    return results
