from rest_framework import serializers
from .models import (
    AutomatedDevice,
    DevelcoDevice,
    DevelcoDeviceData,
    DeviceImage,
    Limits,
)


class DeviceDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DevelcoDeviceData
        fields = [
            "id",
            "key",
            "name",
            "type",
            "unit",
            "access",
            "last_updated",
            "value",
        ]

    def to_internal_value(self, data):
        # Convert the incoming data into a DevelcoDeviceData instance
        data_id = data.get("id")
        try:
            data = DevelcoDeviceData.objects.get(id=data_id)
        except DevelcoDeviceData.DoesNotExist:
            raise serializers.ValidationError("Device data does not exist")
        return data


class DevelcoDeviceSerializer(serializers.ModelSerializer):
    device_data = DeviceDataSerializer(many=True)

    class Meta:
        model = DevelcoDevice
        fields = ["id", "name", "device_id", "device_data"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["device_data"] = representation["device_data"][:100]
        return representation


class DevelcoDeviceStatusSerializer(serializers.ModelSerializer):
    data = DeviceDataSerializer(many=True)

    class Meta:
        model = DevelcoDevice
        fields = ["name", "data"]

    def get_data(self, obj):
        # Get the latest data for the device
        return obj.data


class DeviceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceImage
        fields = ["id", "name", "image_url"]

    def to_internal_value(self, data):
        # Convert the incoming image data into a DeviceImage instance
        image_id = data.get("id")
        try:
            image = DeviceImage.objects.get(id=image_id)
        except DeviceImage.DoesNotExist:
            raise serializers.ValidationError("Image does not exist")
        return image


class AutomatedDeviceSerializer(serializers.ModelSerializer):
    image = DeviceImageSerializer()

    class Meta:
        model = AutomatedDevice
        fields = ["id", "name", "description", "endpoint", "enabled", "image"]

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        return instance


class LimitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Limits
        fields = ["id", "name", "low_value", "high_value", "unit", "image_url"]

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        return instance
