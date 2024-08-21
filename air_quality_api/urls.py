from django.urls import path

from .views import (
    AutomatedDeviceView,
    DevelcoDeviceLimitView,
    DevelcoDeviceStatusView,
    DevelcoDeviceView,
    DeviceDataPredictionView,
    DeviceDataView,
    DeviceImageView,
    ModeView,
    TipsView,
)

urlpatterns = [
    path("device-image/", DeviceImageView.as_view()),
    path("automated-device/<int:id>/", AutomatedDeviceView.as_view()),
    path("automated-device/", AutomatedDeviceView.as_view()),
    path("tips/", TipsView.as_view()),
    path("device-data/", DeviceDataView.as_view()),
    path("device-data-prediction/", DeviceDataPredictionView.as_view()),
    path("develco-device/", DevelcoDeviceView.as_view()),
    path("develco-device/limit/", DevelcoDeviceLimitView.as_view()),
    path("develco-device/limit/<int:id>/", DevelcoDeviceLimitView.as_view()),
    path("develco-device/status/", DevelcoDeviceStatusView.as_view()),
    path("develco-device/<int:id>/", DevelcoDeviceView.as_view()),
    path("mode/", ModeView.as_view()),
]
