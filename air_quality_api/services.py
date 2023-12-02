import json
import requests

from air_quality_api.models import DevelcoDevice, DevelcoDeviceData, Metadata, MetadataDataGroup, NamingSchema, NamingSchemaField
from air_quality_api.utils import *


DEVELCO_API_URL = "http://192.168.0.153"


class DevelcoService(object):
    """
    This class contains methods for getting data from the Develco API.
    """

    @staticmethod
    @functiondelay
    def get_devices_from_api():
        """
        This method gets devices from the Develco API, saves it to the database and returns it.
        """
        print('Getting devices from API')
        # Get the data from the API
        devices = requests.get(DEVELCO_API_URL+'/ssapi/zb/dev').json()
        converted_devices = []
        # For each device in data remove \ from metadata
        for device in devices:
            device['deviceId'] = device.pop('id')
            device['metadata'] = json.loads(
                device['metadata'].replace('\\', ''))
            device = convert_json(device, camel_to_underscore)
            converted_devices.append(device)

        devices = converted_devices

        for device in devices:
            develco_device_fields = DevelcoDevice._meta.get_fields()
            for key in device.copy().keys():
                if not key in [field.name for field in develco_device_fields]:
                    device.pop(key)

            if 'metadata' in device:
                metadata_fields = Metadata._meta.get_fields()
                for key in device['metadata'].copy().keys():
                    if not key in [field.name for field in metadata_fields]:
                        device['metadata'].pop(key)

                if 'naming_schema' in device['metadata']:
                    naming_schema_fields = NamingSchema._meta.get_fields()
                    for key in device['metadata']['naming_schema'].copy().keys():
                        if not key in [field.name for field in naming_schema_fields]:
                            device['metadata']['naming_schema'].pop(key)

                    if 'fields' in device['metadata']['naming_schema']:
                        naming_schema_field_fields = NamingSchemaField._meta.get_fields()
                        for field in device['metadata']['naming_schema']['fields']:
                            for key in field.copy().keys():
                                if not key in [field.name for field in naming_schema_field_fields]:
                                    field.pop(key)

                if 'data_groups' in device['metadata']:
                    data_group_fields = MetadataDataGroup._meta.get_fields()
                    for group in device['metadata']['data_groups']:
                        for key in group.copy().keys():
                            if not key in [field.name for field in data_group_fields]:
                                group.pop(key)

        # check if device already exists by device_id and save it if it doesn't
        database_devices = DevelcoDevice.objects.all()
        devices_to_save = []
        for device in devices:
            if not database_devices.filter(device_id=device['device_id']).exists():
                devices_to_save.append(device)

        devices = devices_to_save

        for device in devices:
            metadata_data = device.pop('metadata')

            data_groups = []

            if 'data_groups' in metadata_data:
                for group_data in metadata_data.pop('data_groups'):
                    group = MetadataDataGroup.objects.create(**group_data)
                    data_groups.append(group)

            if 'naming_schema' in metadata_data:
                fields = []
                if 'fields' in metadata_data['naming_schema']:
                    for field in metadata_data['naming_schema'].pop('fields'):
                        fields.append(
                            NamingSchemaField.objects.create(**field))
                metadata_data['naming_schema'] = NamingSchema.objects.create(
                    **metadata_data['naming_schema'])
                metadata_data['naming_schema'].fields.set(fields)
                metadata_data['naming_schema'].save()

            metadata = Metadata.objects.create(**metadata_data)
            metadata.data_groups.set(data_groups)
            metadata.save()

            device = DevelcoDevice.objects.create(**device)
            device.metadata = metadata
            device.save()

        return devices

    @staticmethod
    @functiondelay
    def get_device_data_from_api(device_id, data_name):
        """
        This method gets device data from the Develco API, saves it to the database and returns it.
        """
        # Get the data from the API
        data = requests.get(
            DEVELCO_API_URL+f'/ssapi/zb/dev/{device_id}/ldev/{data_name}/data').json()

        data = convert_json(data, camel_to_underscore)
        if isinstance(data, list) and 'code' in data[0] and data[0]['code'] == 106:
            return None

        print(data)
        # Map the data to the model
        data = [DevelcoDeviceData(**device) for device in data]
        # Check if the device already exists by last_updated and key fields in the database and save it if it doesn't
        database_device_data = DevelcoDeviceData.objects.all()
        for device in data:
            if not database_device_data.filter(last_updated=device.last_updated, key=device.key).exists():
                device = device.save()
        # Return the data
        return data

    @staticmethod
    @functiondelay
    def get_device_data_for_all_devices():
        """
        This method gets device data from the Develco API, saves it to the database and returns it.
        """
        # Get devices from the database
        devices = DevelcoDevice.objects.all()
        # Get the data from the API for all devices
        data_to_return = []
        for device in devices:
            for data_group in device.metadata.data_groups.all():
                print(DEVELCO_API_URL +
                      f'/ssapi/zb/dev/{device.device_id}/ldev/{data_group.ldev_key}/data')
                data = DevelcoService.get_device_data_from_api(
                    device.id, data_group.ldev_key)
                if data:
                    data_to_return.append(data)
        return data_to_return

    @staticmethod
    @functiondelay
    def check_for_devices_in_database():
        """
        This method checks if there are any devices in the database and if not, it gets devices from the API and saves them to the database.
        """
        # Check if there are any devices in the database
        if not DevelcoDevice.objects.all().exists():
            # Get devices from the API and save them to the database
            DevelcoService.get_devices_from_api()
