# Generated by Django 4.1.7 on 2023-11-02 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('air_quality_api', '0005_rename_manufacturer_develcodevice_manufacturer_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='develcodevice',
            name='device_id',
            field=models.IntegerField(null=True),
        ),
    ]
