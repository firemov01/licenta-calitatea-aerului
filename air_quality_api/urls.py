from django.urls import path
from .views import (GraphDataView, ScriptView)

urlpatterns = [
    path('graph_data/', GraphDataView.as_view()),
    path('script/', ScriptView.as_view()),
]
