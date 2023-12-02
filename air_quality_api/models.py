import json
from typing import Any
from django.db import models
from django.contrib.auth.models import User

# TODO: Remove this


class GraphData(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.name


# TODO: Remove this
class GraphValue(models.Model):
    id = models.AutoField(primary_key=True)
    value = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
    graph_data = models.ForeignKey(GraphData, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return super().__str__()


class NamingSchemaField(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    placeholder = models.CharField(max_length=200)

    def __str__(self) -> str:
        return super().__str__()


class NamingSchema(models.Model):
    id = models.AutoField(primary_key=True)
    use_locale = models.BooleanField()
    separator = models.CharField(max_length=200)
    fields = models.ManyToManyField(NamingSchemaField)

    def __str__(self) -> str:
        return super().__str__()


class MetadataDataGroup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    placement = models.IntegerField()
    ldev_key = models.CharField(max_length=200)
    dp_key = models.CharField(max_length=200)

    def __str__(self) -> str:
        return super().__str__()


class Metadata(models.Model):
    id = models.AutoField(primary_key=True)
    img_url = models.CharField(max_length=200)
    naming_schema = models.ForeignKey(
        NamingSchema, on_delete=models.CASCADE, null=True)
    data_groups = models.ManyToManyField(MetadataDataGroup)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return super().__str__()


class DevelcoDeviceData(models.Model):
    # id from the database
    id = models.AutoField(primary_key=True)
    # key
    key = models.CharField(max_length=200)
    # name
    name = models.CharField(max_length=200)
    # type
    type = models.CharField(max_length=200)
    # unit
    unit = models.CharField(max_length=200)
    # access
    access = models.CharField(max_length=200)
    # last updated
    last_updated = models.DateTimeField()
    # value
    value = models.FloatField()

    def __str__(self) -> str:
        return self.name


class DevelcoDevice(models.Model):
    # id from the database
    id = models.AutoField(primary_key=True)
    # name of the device
    name = models.CharField(max_length=200)
    # device id
    device_id = models.IntegerField(null=True)
    # eui
    eui = models.CharField(max_length=200)
    # manufacturer name
    manufacturer_name = models.CharField(max_length=200)
    # model identifier
    model_identifier = models.CharField(max_length=200)
    # default name of the device
    default_name = models.CharField(max_length=200)
    # metadata
    metadata = models.ForeignKey(Metadata, on_delete=models.CASCADE, null=True)
    # template hash - a hash of the template
    template_hash = models.CharField(max_length=200)
    # discovered - is the device discovered
    discovered = models.BooleanField()
    # online - is the device online
    online = models.BooleanField()
    # config complete pct (percentage) - how much of the configuration is complete
    config_complete_pct = models.IntegerField()
    # device data
    device_data = models.ManyToManyField(DevelcoDeviceData)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return self.name
