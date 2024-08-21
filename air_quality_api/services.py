import os
import joblib
from datetime import datetime, timedelta
import json
import requests
from air_quality_api.models import (
    AutomatedDevice,
    DevelcoDevice,
    DevelcoDeviceData,
    IsAutomaticModeActive,
    Limits,
    Metadata,
    MetadataDataGroup,
    NamingSchema,
    NamingSchemaField,
)
from air_quality_api.utils import *


DEVELCO_API_URL = "http://192.168.2.10"


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
        print("Getting devices from API")
        devices = None
        try:
            # Get the data from the API
            devices = requests.get(DEVELCO_API_URL + "/ssapi/zb/dev").json()
            converted_devices = []
            # For each device in data remove \ from metadata
            for device in devices:
                if device["online"] and device["discovered"]:
                    device["deviceId"] = device.pop("id")
                    device["metadata"] = json.loads(
                        device["metadata"].replace("\\", "")
                    )
                    device = convert_json(device, camel_to_underscore)
                    converted_devices.append(device)

            devices = converted_devices

            for device in devices:
                develco_device_fields = DevelcoDevice._meta.get_fields()
                for key in device.copy().keys():
                    if not key in [field.name for field in develco_device_fields]:
                        device.pop(key)

                if "metadata" in device:
                    metadata_fields = Metadata._meta.get_fields()
                    for key in device["metadata"].copy().keys():
                        if not key in [field.name for field in metadata_fields]:
                            device["metadata"].pop(key)

                    if "naming_schema" in device["metadata"]:
                        naming_schema_fields = NamingSchema._meta.get_fields()
                        for key in device["metadata"]["naming_schema"].copy().keys():
                            if not key in [
                                field.name for field in naming_schema_fields
                            ]:
                                device["metadata"]["naming_schema"].pop(key)

                        if "fields" in device["metadata"]["naming_schema"]:
                            naming_schema_field_fields = (
                                NamingSchemaField._meta.get_fields()
                            )
                            for field in device["metadata"]["naming_schema"]["fields"]:
                                for key in field.copy().keys():
                                    if not key in [
                                        field.name
                                        for field in naming_schema_field_fields
                                    ]:
                                        field.pop(key)

                    if "data_groups" in device["metadata"]:
                        data_group_fields = MetadataDataGroup._meta.get_fields()
                        for group in device["metadata"]["data_groups"]:
                            for key in group.copy().keys():
                                if not key in [
                                    field.name for field in data_group_fields
                                ]:
                                    group.pop(key)

            # check if device already exists by device_id and save it if it doesn't
            database_devices = DevelcoDevice.objects.all()
            devices_to_save = []
            for device in devices:
                if not database_devices.filter(device_id=device["device_id"]).exists():
                    devices_to_save.append(device)

            devices = devices_to_save

            for device in devices:
                metadata_data = device.pop("metadata")

                data_groups = []

                if "data_groups" in metadata_data:
                    for group_data in metadata_data.pop("data_groups"):
                        group = MetadataDataGroup.objects.create(**group_data)
                        data_groups.append(group)

                if "naming_schema" in metadata_data:
                    fields = []
                    if "fields" in metadata_data["naming_schema"]:
                        for field in metadata_data["naming_schema"].pop("fields"):
                            fields.append(NamingSchemaField.objects.create(**field))
                    metadata_data["naming_schema"] = NamingSchema.objects.create(
                        **metadata_data["naming_schema"]
                    )
                    metadata_data["naming_schema"].fields.set(fields)
                    metadata_data["naming_schema"].save()

                metadata = Metadata.objects.create(**metadata_data)
                metadata.data_groups.set(data_groups)
                metadata.save()

                device = DevelcoDevice.objects.create(**device)
                device.metadata = metadata
                device.save()

            return devices
        except Exception as e:
            print(devices)
            raise e

    @staticmethod
    @functiondelay
    def get_device_data_from_api(device_id, data_name):
        """
        This method gets device data from the Develco API, saves it to the database and returns it.
        """
        # Get the data from the API
        data = requests.get(
            DEVELCO_API_URL + f"/ssapi/zb/dev/{device_id}/ldev/{data_name}/data"
        ).json()

        data = convert_json(data, camel_to_underscore)
        if isinstance(data, list) and "code" in data[0] and data[0]["code"] == 106:
            print("No data for device with id: " + str(device_id))
            print(data)
            return None

        print(data)
        # Map the data to the model and the id of the device
        data = [
            DevelcoDeviceData(**device, develco_device_id=device_id) for device in data
        ]
        # Check if the device already exists by last_updated and key fields in the database and save it if it doesn't
        database_device_data = DevelcoDeviceData.objects.all()
        for device in data:
            if not database_device_data.filter(
                last_updated=device.last_updated,
                key=device.key,
                develco_device_id=device_id,
            ).exists():
                device = device.save()
        # Return the data
        return data

    @staticmethod
    @functiondelay
    def get_device_data_for_all_devices():
        """
        This method gets device data from the Develco API, saves it to the database and returns it.
        """
        # Update database
        DevelcoService.get_devices_from_api()
        # Get devices from the database
        devices = DevelcoDevice.objects.all()
        # Get the data from the API for all devices
        data_to_return = []
        for device in devices:
            if device.online and device.discovered:
                print(str(device))
                for data_group in device.metadata.data_groups.all():
                    print(
                        DEVELCO_API_URL
                        + f"/ssapi/zb/dev/{device.device_id}/ldev/{data_group.ldev_key}/data"
                    )
                    data = DevelcoService.get_device_data_from_api(
                        device.device_id, data_group.ldev_key
                    )
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


class TipsService(object):
    """
    This class contains methods for getting tips.
    """

    @staticmethod
    def get_tips():
        """
        This method returns the tips.
        """
        number_of_days = 90
        # Get humidity, temperature and voc data from last 30 days
        humidity_data = DevelcoDeviceData.objects.filter(
            key="humidity",
            last_updated__gte=datetime.now() - timedelta(days=number_of_days),
        )
        temperature_data = DevelcoDeviceData.objects.filter(
            key="temperature",
            last_updated__gte=datetime.now() - timedelta(days=number_of_days),
        )
        voc_data = DevelcoDeviceData.objects.filter(
            key="voc", last_updated__gte=datetime.now() - timedelta(days=number_of_days)
        )

        tips = []
        # Best temperature is 20 degrees if it is above 20 degrees recommend opening a window if it's cold enough outside or to get an air conditioner. If the temperature is lower than 20 degrees turn on the heat
        if temperature_data.exists():
            # Get the average temperature
            temperature = sum(
                [
                    0 if data.value == "" else float(data.value)
                    for data in temperature_data
                ]
            ) / len(temperature_data)
            if temperature > 21:
                tips.append(
                    "Open a window if it's cold enough outside or get an air conditioner."
                )
            elif temperature < 19:
                tips.append("Turn on the heat.")
            else:
                tips.append("The temperature is good.")

        # The best humidity is between 40 and 60 percent. If the humidity is above 60 percent recommend opening a window or turning on the air conditioner. If the humidity is below 40 percent recommend using a humidifier.
        if humidity_data.exists():
            # Get the average humidity
            humidity = sum(
                [0 if data.value == "" else float(data.value) for data in humidity_data]
            ) / len(humidity_data)
            if humidity > 60:
                tips.append("Open a window or turn on the air conditioner.")
            elif humidity < 40:
                tips.append("Use a humidifier.")
            else:
                tips.append("The humidity is good.")

        # The best VOC level is below 400. If the VOC level is above 400 recommend opening a window or turning on the air purifier.
        if voc_data.exists():
            # Get the average VOC level
            voc = sum(
                [0 if data.value == "" else float(data.value) for data in voc_data]
            ) / len(voc_data)
            if voc > 400:
                tips.append("Open a window or turn on the air purifier.")
            else:
                tips.append("The air quality is good.")

        return tips


class PredictionService(object):
    """
    Singleton class for getting predictions.
    """

    __instance = None
    __model = None

    def __new__(cls):
        if cls.__instance is None or cls.__model is None:
            cls.__instance = super(PredictionService, cls).__new__(cls)
            cls.__model = joblib.load(
                os.path.join(os.path.dirname(__file__), "model.pkl")
            )
        return cls.__instance

    def get_prediction(self, date):
        """
        Method to get prediction.
        """

        # split the date in year, month, day, hour
        year = date.year
        month = date.month
        day = date.day
        hour = date.hour

        # Add your prediction logic here
        prediction = self.__model.predict([[year, month, day, hour]])

        return prediction

    def get_predictions(self, dates):
        """
        Method to get predictions.
        """

        splited_dates = []
        for date in dates:
            year = date.year
            month = date.month
            day = date.day
            hour = date.hour
            splited_dates.append([year, month, day, hour])

        predictions = self.__model.predict(splited_dates)

        return predictions

    # Usage:
    # prediction_service = PredictionService()
    # predictions = prediction_service.get_predictions()


class AutomationService(object):
    """
    This class contains methods for automating devices.
    """

    shelly_ip = "192.168.0.180"

    @staticmethod
    def automate_devices():
        """
        This method automates a device.
        """
        # Get all AutomatedDevices from the database
        automated_devices = AutomatedDevice.objects.all().filter(enabled=True)
        # make a list from automated_devices
        automated_device = list(automated_devices)
        print(automated_device[0].image.name)

        if len(automated_device) == 0:
            return

        if not IsAutomaticModeActive.objects.first().is_active:
            for automated_device in automated_devices:
                requests.get(f"http://{automated_device.endpoint}/relay/0?turn=off")
            return

        # Get the data from the prediction service for the next hour
        prediction_service = PredictionService()
        prediction = prediction_service.get_prediction(
            datetime.now() + timedelta(hours=1)
        )
        prediction = prediction[0]

        for automated_device in automated_devices:

            # Get the data from the database
            limit = None
            # "Air Conditioner" "Heater" "Humidifier" "Dehumidifier" "Air Purifier"
            if automated_device.image.name == "Air Conditioner":
                print("here")
                limit = Limits.objects.get(name="Temperature")
                # If the temperature is above the limit, turn on the device
                if prediction[3] > limit.high_value:
                    requests.get(f"http://{automated_device.endpoint}/relay/0?turn=on")
                else:
                    requests.get(f"http://{automated_device.endpoint}/relay/0?turn=off")
                print(limit.high_value, prediction[3])
            elif automated_device.image.name == "Heater":
                limit = Limits.objects.get(name="Temperature")
                # If the temperature is below the limit, turn on the device
                if prediction[3] < limit.low_value:
                    requests.get(f"http://{automated_device.endpoint}/relay/0?turn=on")
                else:
                    requests.get(f"http://{automated_device.endpoint}/relay/0?turn=off")
            elif automated_device.image.name == "Humidifier":
                limit = Limits.objects.get(name="Humidity")
                # If the humidity is below the limit, turn on the device
                if prediction[0] < limit.low_value:
                    requests.get(f"http://{automated_device.endpoint}/relay/0?turn=on")
                else:
                    requests.get(f"http://{automated_device.endpoint}/relay/0?turn=off")
            elif automated_device.image.name == "Dehumidifier":
                limit = Limits.objects.get(name="Humidity")
                # If the humidity is above the limit, turn on the device
                if prediction[0] > limit.high_value:
                    requests.get(f"http://{automated_device.endpoint}/relay/0?turn=on")
                else:
                    requests.get(f"http://{automated_device.endpoint}/relay/0?turn=off")
            elif automated_device.image.name == "Air Purifier":
                limit = Limits.objects.get(name="VOC")
                # If the VOC is above the limit, turn on the device
                if prediction[4] > limit.high_value:
                    requests.get(f"http://{automated_device.endpoint}/relay/0?turn=on")
                else:
                    requests.get(f"http://{automated_device.endpoint}/relay/0?turn=off")
