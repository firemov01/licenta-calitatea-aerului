# Generated by Django 4.1.7 on 2024-03-05 12:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('air_quality_api', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='develcodevice',
            name='device_data',
        ),
    ]
