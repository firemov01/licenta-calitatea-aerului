import json
from develcoapi import DevelcoApi
import os, schedule

develcoapi = DevelcoApi('http://gw-2a00.local')
devices = develcoapi.get_zigbee_devices()
# for device in devices:
#     for dataGroup in json.loads(develcoapi.get_zigbee_device(device.id)['metadata'])['dataGroups']:
#         # print(dataGroup['ldevKey'])
#         for data in develcoapi.get_zigbee_device_data(device.id, dataGroup['ldevKey']):
#             print(f'{data.name} {data.unit}, {data.value}')
    # print()

# check if ./data.csv exists if exists check if it is empty if it doesn't exist create it, if is empty write the header. Header should be {data.name} {data.unit}

def writeDataToFile():
    with open('./data.csv', 'a') as f:
        for device in devices:
            for dataGroup in json.loads(develcoapi.get_zigbee_device(device.id)['metadata'])['dataGroups']:
                    for data in develcoapi.get_zigbee_device_data(device.id, dataGroup['ldevKey']):
                        f.write(f'{data.value},')
        f.seek(f.tell() - 1, os.SEEK_SET)
        f.truncate()
        f.write('\n')
        f.close()

def writeHeader():
    with open('./data.csv', 'w') as f:
            for device in devices:
                for dataGroup in json.loads(develcoapi.get_zigbee_device(device.id)['metadata'])['dataGroups']:
                    for data in develcoapi.get_zigbee_device_data(device.id, dataGroup['ldevKey']):
                        unit = data.unit or ""
                        f.write(f'{data.name} {unit},')
            f.seek(f.tell() - 1, os.SEEK_SET)
            f.truncate()
            f.write('\n')
            f.close()

if os.path.exists('./data.csv'):
    if os.stat('./data.csv').st_size == 0:
        writeHeader()
else:
    writeHeader()
    

# schedule a task to run every 15 minutes and write the data to the file
writeDataToFile()
schedule.every(15).minutes.do(writeDataToFile)
while True:
    schedule.run_pending()