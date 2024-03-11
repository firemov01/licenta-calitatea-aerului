from django.urls import path
from .views import (DevelcoDeviceView, DeviceDataView)

urlpatterns = [
    path('device_data/', DeviceDataView.as_view()),
    path('develco_device/', DevelcoDeviceView.as_view()),
    path('develco_device/<int:id>/', DevelcoDeviceView.as_view()),
]
