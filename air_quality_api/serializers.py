import logging
import sys
from rest_framework import serializers
from .models import DevelcoDevice, DevelcoDeviceData


class DeviceDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DevelcoDeviceData
        fields = ['id', 'key', 'name', 'type',
                  'unit', 'access', 'last_updated', 'value']


class DevelcoDeviceSerializer(serializers.ModelSerializer):
    device_data = serializers.SerializerMethodField()

    class Meta:
        model = DevelcoDevice
        fields = ['id', 'name', 'device_id', 'device_data']

    def get_device_data(self, obj):
        logger = logging.getLogger('django')
        logger.info(obj.__dict__)
        device_data = DevelcoDeviceData.objects.filter(
            develco_device_id=obj.device_id)
        serializer = DeviceDataSerializer(device_data, many=True)
        return serializer.data
