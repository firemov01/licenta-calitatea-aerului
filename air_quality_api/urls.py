from django.urls import path
from .views import (DeviceDataView, GraphDataView, ScriptView)

urlpatterns = [
    path('device_data/', DeviceDataView.as_view()),
    # path('graph_data/', GraphDataView.as_view()),
    # path('script/', ScriptView.as_view()),
]
