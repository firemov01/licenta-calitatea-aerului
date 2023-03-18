import time
import requests, json

class ZigBeeDeviceApi():
    def __init__(self, eui, manufacturerName, modelIdentifier, id, name, defaultName, metadata, templateHash, discovered, online, configCompletePct, version=None):
        self.eui = eui
        self.manufacturerName = manufacturerName
        self.modelIdentifier = modelIdentifier
        self.id = id
        self.name = name
        self.defaultName = defaultName
        self.metadata = metadata
        self.templateHash = templateHash
        self.discovered = discovered
        self.online = online
        self.configCompletePct = configCompletePct
        self.version = version

        if(self.metadata):
            self.metadata = json.loads(self.metadata)
    
    def toString(self):
        return f'eui:{self.eui}, manufacturerName:{self.manufacturerName}, modelIdentifier:{self.modelIdentifier}, id:{self.id}, name:{self.name}, defaultName:{self.defaultName}, metadata:{self.metadata}, templateHash:{self.templateHash}, discovered:{self.discovered}, online:{self.online}, configCompletePct:{self.configCompletePct}, version:{self.version}'

class DeviceData():
    # DeviceData have fields: key, name, type, access, lastUpdated, value and sometimes unit
    def __init__(self, key, name, type, access, lastUpdated, value, unit=None):
        self.key = key
        self.name = name
        self.type = type
        self.access = access
        self.lastUpdated = lastUpdated
        self.value = value
        self.unit = unit


class DevelcoApi():
    def __init__(self, gateway_url):
        self.gateway_url = gateway_url

    def functiondelay(function):
        def wrapper(*args, **kwargs):
            time.sleep(0.5)
            return function(*args, **kwargs)
        wrapper.nodelay = function
        return wrapper

    @functiondelay
    def get_zigbee_devices(self):
        response = requests.get(self.gateway_url + '/ssapi/zb/dev')
        zigbee_devices = response.json()
        zigbee_devices = [ZigBeeDeviceApi(**zigbee_device) for zigbee_device in zigbee_devices]
        response.close()
        return zigbee_devices

    @functiondelay
    def get_zigbee_device_data(self, id, dataName):
        url = self.gateway_url+'/ssapi/zb/dev/'+str(id)+'/ldev/'+dataName+'/data'
        response = requests.get(url)
        zigbee_device_data = response.json()
        zigbee_device_data = [DeviceData(**zdd) for zdd in zigbee_device_data]
        response.close()
        return zigbee_device_data

    @functiondelay
    def get_zigbee_device(self, id):
        response = requests.get(self.gateway_url + '/ssapi/zb/dev/'+str(id))
        zigbee_device = response.json()
        # zigbee_device = ZigBeeDeviceApi(**zigbee_device)
        response.close()
        return zigbee_device