from __future__ import absolute_import, unicode_literals

from celery import shared_task
from celery import signals


@signals.worker_ready.connect
def at_start(sender, **k):
    print("Celery worker started")
    # get devices from the API and save them to the database
    from .services import DevelcoService, AutomationService

    DevelcoService.get_devices_from_api()
    AutomationService.automate_devices()


@shared_task
def get_device_data_for_all_devices():
    print("Getting device data for all devices")
    from .services import DevelcoService

    DevelcoService.get_device_data_for_all_devices()


@shared_task
def automate_devices():
    from .services import AutomationService

    AutomationService.automate_devices()
