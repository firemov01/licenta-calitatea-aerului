import datetime
import json
import os
import threading
from time import sleep
import schedule
from air_quality_api.models import GraphData, GraphValue
from django.shortcuts import get_object_or_404

from air_quality_api.data_script.develcoapi import DevelcoApi


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DataScript(metaclass=Singleton):
    def __init__(self):
        self.thread = None
        self.is_running = False
        self.develcoapi = DevelcoApi('http://192.168.0.153')
        self.devices = self.develcoapi.get_zigbee_devices()
        if os.path.exists('./data.csv'):
            if os.stat('./data.csv').st_size == 0:
                self.writeHeader()
        else:
            self.writeHeader()
        self.writeDataToFile()
        schedule.every(15).minutes.do(self.writeDataToFile)

    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def stop(self):
        self.is_running = False

    def writeDataToFile(self):
        with open('./data.csv', 'a') as f:
            # write date
            f.write(f'{datetime.datetime.now()},')
            for device in self.devices:
                for dataGroup in json.loads(self.develcoapi.get_zigbee_device(device.id)['metadata'])['dataGroups']:
                    for data in self.develcoapi.get_zigbee_device_data(device.id, dataGroup['ldevKey']):
                        # should save a GraphValue in DB
                        d = GraphData.objects.get(
                            name=f'{data.name} {data.unit or ""}')
                        v = GraphValue(graph_data=d, value=data.value)
                        v.save()
                        f.write(f'{data.value},')
            f.seek(f.tell() - 1, os.SEEK_SET)
            f.truncate()
            f.write('\n')
            f.close()

    def writeHeader(self):
        with open('./data.csv', 'w') as f:
            # write current datetime
            f.write('DateTime,')
            while len(self.devices) == 0:
                sleep(0.5)
            for device in self.devices:
                for dataGroup in json.loads(self.develcoapi.get_zigbee_device(device.id)['metadata'])['dataGroups']:
                    for data in self.develcoapi.get_zigbee_device_data(device.id, dataGroup['ldevKey']):
                        unit = data.unit or ""
                        # should save a GraphData in the db with name=f'{data.name} {unit}' and id=device.id if there is none
                        if len(GraphData.objects.filter(name=f'{data.name} {unit}')) == 0:
                            d = GraphData(name=f'{data.name} {unit}')
                            d.save()
                        f.write(f'{data.name} {unit},')
            f.seek(f.tell() - 1, os.SEEK_SET)
            f.truncate()
            f.write('\n')
            f.close()

    def run(self):
        self.is_running = True
        while self.is_running:
            schedule.run_pending()
